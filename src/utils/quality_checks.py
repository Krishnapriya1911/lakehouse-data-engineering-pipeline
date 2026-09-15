def validate_orders(df):
    """
    Runs basic data quality checks
    """

    # Check negative amounts
    negative_amounts = df.filter(df.amount <= 0).count()

    # Check null order IDs
    null_order_ids = df.filter(df.order_id.isNull()).count()

    print("\nQUALITY CHECK RESULTS")
    print(f"Negative Amount Records: {negative_amounts}")
    print(f"Null Order IDs: {null_order_ids}")

    if negative_amounts == 0 and null_order_ids == 0:
        print("All quality checks passed!")
    else:
        print("Data quality issues detected!")