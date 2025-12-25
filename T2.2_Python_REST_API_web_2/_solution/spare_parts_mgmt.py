#!/home/expert/venvs/main/bin/python

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
        "N9K-C9364C": {"amount": 7, "price": 50000, "backorder": 0},
        "N9K-C93180YC-FX3": {"amount": 8, "price": 50000, "backorder": 0},
    },
    max_capacity=60,
    cash_balance=1000000,
    motd="Spare Parts Robot ready for service.",
)

# Part Request Parser
part_parser = reqparse.RequestParser(bundle_errors=True)
part_parser.add_argument("part", required=True, type=str)
part_parser.add_argument("amount", type=int, required=True)

# Cash Request Parser
cash_parser = reqparse.RequestParser(bundle_errors=True)
cash_parser.add_argument("amount", type=int, required=True)

# Capacity Request Parser
capacity_parser = reqparse.RequestParser(bundle_errors=True)
capacity_parser.add_argument("parameter", required=True, type=str)

# Motd Request Parser
motd_parser = reqparse.RequestParser(bundle_errors=True)
motd_parser.add_argument("msg", required=True, type=str)

# TODO (T2.2 Extension 2)
# 1) Deprecate the /motd endpoint in Swagger so users know changes are coming.
# 2) In /cash DELETE, when Machine.remove_cash(amount) fails, return HTTP 404 (not 200).
# 3) Ensure Swagger shows BOTH response models for /cash DELETE: 200 and 404.

gen_response_model = api.model(
    "gen_response",
    {
        "success": fields.Boolean(required=True, choices={False, True}),
        "message": fields.String(required=True),
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

# TODO
# Deprecate /motd endpoint in Swagger (e.g., @api.doc(deprecated=True))
@api.doc(deprecated=True)
class motd(Resource):
    """API Class for motd."""

    def get(self):
        """Retrieve motd."""
        return Machine.get_motd()

class capacity(Resource):
    """API Class for capacity."""

    def get(self):
        """Return the max capacity of the machine."""
        parameter = capacity_parser.parse_args()["parameter"]
        if parameter == "max":
            return Machine.get_max_capacity(), 200
        elif parameter == "current":
            return Machine.get_current_capacity(), 200
        else:
            return "Invalid parameter", 400

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
            return handle_gen_resp("Cash added to the robot", True, gen_response_model)
        else:
            return handle_gen_resp(
                "Unable to add cash to the robot", False, gen_response_model
            )

    @api.expect(cash_parser, validate=True)
    @api.response(404, "Machine cannot provide cash, out of balance reached", gen_response_model)
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
            # TODO: return HTTP 404 in this scenario, and document 404 response model in Swagger.
            return handle_gen_resp(
                "Machine cannot provide cash, out of balance reached",
                False,
                gen_response_model,
                http_resp=404,
            )

class part(Resource):
    """API Class for part."""

    @api.expect(part_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Add part response")
    def post(self):
        """Add part(s) to the stock."""
        args = part_parser.parse_args()

        part = args["part"]
        amount = args["amount"]

        if Machine.add_part(part, amount):
            return handle_gen_resp("Part added to inventory", True, gen_response_model)
        else:
            return handle_gen_resp(
                "Stock is out of capacity", False, gen_response_model
            )

    @api.expect(part_parser, validate=True)
    @api.marshal_with(gen_response_model, code=200, description="Remove part response")
    def delete(self):
        """Remove part(s) from the stock."""
        args = part_parser.parse_args()

        part = args["part"]
        amount = args["amount"]

        backorder = Machine.get_backorder(part)

        if Machine.remove_part(part, amount):
            if backorder:
                Machine.backorder_part(part, backorder)
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
api.add_resource(part, "/part", endpoint="part")
api.add_resource(cash, "/cash", endpoint="cash")
api.add_resource(capacity, "/capacity", endpoint="capacity")
api.add_resource(motd, "/motd", endpoint="motd")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, processes=1, host="0.0.0.0", port=4242)
