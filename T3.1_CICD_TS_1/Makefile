clean:
    rm -rf results/*

lookup-mock:
    pyats parse "show processes cpu" \
      --testbed testbeds/testbed-mock.yaml \
      --output results

lookup-prod:
    pyats parse "show processes cpu" \
      --testbed testbeds/testbed.yaml \
      --output results
