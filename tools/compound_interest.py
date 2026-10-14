import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def parse_decimal(value: str) -> Decimal:
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise argparse.ArgumentTypeError("must be a number") from error

    if not number.is_finite():
        raise argparse.ArgumentTypeError("must be a finite number")
    return number


def calculate_compound_interest(
    principal: Decimal,
    annual_rate: Decimal,
    compounds_per_year: int,
    total_years: Decimal,
) -> tuple[Decimal, Decimal]:
    if principal < 0:
        raise ValueError("principal must be non-negative")
    if annual_rate < 0:
        raise ValueError("annual rate must be non-negative")
    if compounds_per_year <= 0:
        raise ValueError("compounds per year must be greater than zero")
    if total_years < 0:
        raise ValueError("total years must be non-negative")

    final_amount = principal * (
        Decimal(1) + annual_rate / compounds_per_year
    ) ** (compounds_per_year * total_years)
    return final_amount, final_amount - principal


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate compound interest. Enter the annual rate as a "
        "decimal (for example, 0.05 for 5%)."
    )
    parser.add_argument("principal", type=parse_decimal, help="initial principal")
    parser.add_argument(
        "annual_rate", type=parse_decimal, help="annual rate as a decimal"
    )
    parser.add_argument(
        "compounds_per_year", type=int, help="number of compounding periods per year"
    )
    parser.add_argument(
        "total_years", type=parse_decimal, help="total investment duration in years"
    )
    args = parser.parse_args()

    try:
        final_amount, interest_earned = calculate_compound_interest(
            args.principal,
            args.annual_rate,
            args.compounds_per_year,
            args.total_years,
        )
    except ValueError as error:
        parser.error(str(error))

    cents = Decimal("0.01")
    print(
        f"Final amount: "
        f"${final_amount.quantize(cents, rounding=ROUND_HALF_UP):,.2f}"
    )
    print(
        f"Interest earned: "
        f"${interest_earned.quantize(cents, rounding=ROUND_HALF_UP):,.2f}"
    )


if __name__ == "__main__":
    main()
