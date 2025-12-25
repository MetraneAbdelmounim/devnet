from flask import Flask
from flask_restx import Resource, Api, fields, reqparse, marshal, model

from spare_parts_robot import SparePartsRobot

from typing import Any

app = Flask("Spare Parts Robot")

api = Api(
    app,
    version="1.0",
    title="Spare Parts Robot",
    description="Spare Parts Robot",
    prefix="/",
    doc="/doc",
)

Machine = SparePartsRobot(
    inventory={
        "APIC-M3": {"amount": 5, "price": 50000, "backorder": 0},
        "N9K-C9364C": {"amount": 7, "price": 5000, "backorder": 0},
        "N9K-C93180YC-FX3": {"amount": 8, "price": 5000, "backorder": 0},
    },
    max_capacity=60,
    cash_balance=100000,
    motd="Spare Parts Robot ready for service.",
)

# ----------- Parsers -----------

part_parser = reqparse.RequestParser(bundle_errors=True)
part_parser.add_argument("part", required=True, type=str)
part_parser.add_argument("amount", type=int, required=True)

cash_parser = reqparse.RequestParser(bundle_errors=True)
cash_parser.add_argument("amount", type=int, required=True)

capacity_parser = reqparse.RequestParser(bundle_errors=True)
capacity_parser.add_argument("parameter", required=True, type=str)

motd_parser = reqparse.RequestParser(bundle_errors=True)
motd_parser.add_argument("msg", required=True, type=str)

# ----------- Models -----------

gen_response_model = api.model(
    "gen_response",
    {
        "success": fields.Boolean(required=True, choices=(False, True)),
        "message": fields.String(required=True),
    },
)

# Model for a single spare part (REUSED, do not change according to task)
part_model = api.model(
    "part",
    {
        "name": fields.String(required=True, description="Part number"),
        "amount": fields.Integer(required=True, description="Quantity of this part"),
        "price": fields.Integer(required=True, description="Price of this part"),
        "backorder": fields.Integer(required=True, description="Backordered amount"),
    },
)

# TODO:
# Define parts_response_model so that it correctly models the response of the
# /parts endpoint and can be used to document and enforce the GET /parts API.
# Correct model for GET /parts response:
# {
#   "parts": [{name, amount, price, backorder}, ... ]
# }
parts_response_model = api.model(
    "parts_response",
    {
        "parts" : fields.List(
            fields.Nested(part_model),
            required = True,
            description = "List of all spare parts"
        )
    },
)


class inventory(Resource):
    """API Class for inventory."""

    def get(self):
        """Display spare parts inventory."""
        inventory = Machine.getContent()
        current_capacity = Machine.get_current_capacity()
        max_capacity = Machine.get_max_capacity()
        cash_balance = Machine.get_cash_balance()
        return {
            "inventory": inventory,
            "current_capacity": current_capacity,
            "max_capacity": max_capacity,
            "cash_balance": cash_balance,
        }


class parts(Resource):
    """API Class for parts."""

    @api.marshal_with(
        parts_response_model, code=200, description="List of all spare parts"
    )
    def get(self):
        """Return all parts."""
        # Use helper from SparePartsRobot for clarity
        parts_list = Machine.get_parts()
        return {"parts": parts_list}


def handle_gen_resp(
    msg: str, success: bool, response_model: model.Model, http_resp: int = 200
) -> tuple[dict[str, Any], int]:
    """Function provides response for API call."""
    return (
        marshal(
            {"message": msg, "success": success},
            response_model,
        ),
        http_resp,
    )


class motd(Resource):
    """API Class for motd."""

    def get(self):
        """Retrieve motd."""
        return Machine.get_motd()


class capacity(Resource):
    """API Class for capacity."""
    # (Whatever existing logic you have here can remain unchanged)
    pass


class cash(Resource):
    """API Class for cash."""

    def get(self):
        """Return the amount of cash in the machine."""
        return Machine.get_cash_balance(), 200

    @api.expect(cash_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Add cash response")
    def post(self):
        """Add cash to machine."""
        args = cash_parser.parse_args()

        amount = args["amount"]

        if Machine.add_cash(amount):
            return handle_gen_resp(
                "Cash added to the robot", True, gen_response_model
            )
        else:
            return handle_gen_resp(
                "Unable to add cash to the robot", False, gen_response_model
            )

    @api.expect(cash_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Remove cash response")
    def delete(self):
        """Remove cash from machine."""
        args = cash_parser.parse_args()

        amount = args["amount"]

        if Machine.remove_cash(amount):
            return handle_gen_resp(
                "Cash removed from the robot", True, gen_response_model
            )
        else:
            return handle_gen_resp(
                "Machine cannot provide cash, out of balance reached",
                False,
                gen_response_model,
            )


class part(Resource):
    """API Class for part."""

    @api.expect(part_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Add part response")
    def post(self):
        """Add part(s) to the stock."""
        args = part_parser.parse_args()

        part_name = args["part"]
        amount = args["amount"]

        if Machine.add_part(part_name, amount):
            return handle_gen_resp(
                "Part added to the inventory", True, gen_response_model
            )
        else:
            current_capacity = Machine.get_current_capacity()
            max_capacity = Machine.get_max_capacity()
            cash_balance = Machine.get_cash_balance()
            return handle_gen_resp(
                "Parts stock max. capacity reached or out of cash. "
                + f" current capacity: {current_capacity} max capacity: {max_capacity}"
                + f" cash_balance {cash_balance}",
                False,
                gen_response_model,
            )

    @api.expect(part_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Remove part response")
    def delete(self):
        """Remove part from stock."""
        args = part_parser.parse_args()

        part_name = args["part"]
        amount = args["amount"]
        backorder = args.get("backorder", False)

        if Machine.remove_part(part_name, amount):
            if backorder:
                Machine.backorder_part(part_name, backorder)
                return handle_gen_resp(
                    "Part removed from inventory and backordered",
                    True,
                    gen_response_model,
                )
            else:
                return handle_gen_resp(
                    "Part removed from inventory", True, gen_response_model
                )
        else:
            return handle_gen_resp(
                "Stock is out of capacity", False, gen_response_model
            )


api.add_resource(inventory, "/inventory", endpoint="inventory")
api.add_resource(parts, "/parts", endpoint="parts")
api.add_resource(part, "/part", endpoint="part")
api.add_resource(cash, "/cash", endpoint="cash")
api.add_resource(capacity, "/capacity", endpoint="capacity")
api.add_resource(motd, "/motd", endpoint="motd")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, processes=1, host="0.0.0.0", port=4242)
