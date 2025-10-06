"""Currency Conversion Service

Handles multi-currency conversion for UK/SA financial planning.

Features:
- Currency conversion between GBP, ZAR, EUR, USD
- Exchange rate management (static initially, API integration planned)
- Base currency handling
- Historical rates (future feature)
"""

from typing import Dict, Optional
from datetime import date, datetime
from enum import Enum


class Currency(str, Enum):
    """Supported currencies."""
    GBP = "GBP"  # British Pound Sterling
    ZAR = "ZAR"  # South African Rand
    EUR = "EUR"  # Euro
    USD = "USD"  # US Dollar


class CurrencySymbol(str, Enum):
    """Currency symbols for display."""
    GBP = "£"
    ZAR = "R"
    EUR = "€"
    USD = "$"


# Static exchange rates (as of 2024-10-06, indicative rates)
# Base currency: GBP
# TODO: Replace with API integration (e.g., exchangerate-api.com, openexchangerates.org)
STATIC_RATES: Dict[str, float] = {
    "GBP": 1.0,      # Base currency
    "ZAR": 24.0,     # 1 GBP = 24 ZAR (approximate)
    "EUR": 1.17,     # 1 GBP = 1.17 EUR (approximate)
    "USD": 1.30,     # 1 GBP = 1.30 USD (approximate)
}

# Cross rates calculated from GBP base
# Key format: (from_currency, to_currency): rate
# Meaning: 1 from_currency = rate to_currency
CROSS_RATES: Dict[tuple, float] = {
    ("USD", "ZAR"): 18.46,  # 1 USD = 18.46 ZAR
    ("EUR", "ZAR"): 20.51,  # 1 EUR = 20.51 ZAR
    ("ZAR", "USD"): 0.054,  # 1 ZAR = 0.054 USD
    ("ZAR", "EUR"): 0.049,  # 1 ZAR = 0.049 EUR
    ("EUR", "USD"): 1.11,   # 1 EUR = 1.11 USD
    ("USD", "EUR"): 0.90,   # 1 USD = 0.90 EUR
}


class CurrencyConverter:
    """Currency conversion service."""

    def __init__(self):
        """Initialize with static rates."""
        self.rates = STATIC_RATES.copy()

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        as_of_date: Optional[date] = None
    ) -> float:
        """
        Get exchange rate from one currency to another.

        Args:
            from_currency: Source currency code (GBP, ZAR, EUR, USD)
            to_currency: Target currency code
            as_of_date: Optional date for historical rates (not implemented yet)

        Returns:
            float: Exchange rate (1 from_currency = X to_currency)

        Example:
            get_exchange_rate("GBP", "ZAR") -> 24.0 (1 GBP = 24 ZAR)
            get_exchange_rate("ZAR", "GBP") -> 0.0417 (1 ZAR = 0.0417 GBP)
        """
        # TODO: Use as_of_date for historical rates once API integrated

        # Same currency
        if from_currency == to_currency:
            return 1.0

        # Check if from_currency is base (GBP)
        if from_currency == "GBP":
            if to_currency in self.rates:
                return self.rates[to_currency]
            raise ValueError(f"Unsupported currency: {to_currency}")

        # Check if to_currency is base (GBP)
        if to_currency == "GBP":
            if from_currency in self.rates:
                return 1.0 / self.rates[from_currency]
            raise ValueError(f"Unsupported currency: {from_currency}")

        # Cross rate (neither is GBP)
        if (from_currency, to_currency) in CROSS_RATES:
            return CROSS_RATES[(from_currency, to_currency)]

        # Calculate cross rate via GBP
        if from_currency in self.rates and to_currency in self.rates:
            # Convert from_currency -> GBP -> to_currency
            from_to_gbp = 1.0 / self.rates[from_currency]
            gbp_to_target = self.rates[to_currency]
            return from_to_gbp * gbp_to_target

        raise ValueError(f"Cannot convert {from_currency} to {to_currency}")

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        as_of_date: Optional[date] = None
    ) -> float:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            as_of_date: Optional date for historical rates

        Returns:
            float: Converted amount

        Example:
            convert_currency(100, "GBP", "ZAR") -> 2400.0 (£100 = R2,400)
            convert_currency(1000, "ZAR", "GBP") -> 41.67 (R1,000 = £41.67)
        """
        rate = self.get_exchange_rate(from_currency, to_currency, as_of_date)
        return amount * rate

    def get_currency_symbol(self, currency: str) -> str:
        """
        Get currency symbol for display.

        Args:
            currency: Currency code (GBP, ZAR, EUR, USD)

        Returns:
            str: Currency symbol (£, R, €, $)
        """
        try:
            return CurrencySymbol[currency].value
        except KeyError:
            return currency  # Return code if symbol not found

    def format_currency(
        self,
        amount: float,
        currency: str,
        include_symbol: bool = True,
        decimal_places: int = 2
    ) -> str:
        """
        Format amount with currency symbol.

        Args:
            amount: Amount to format
            currency: Currency code
            include_symbol: Whether to include currency symbol
            decimal_places: Number of decimal places

        Returns:
            str: Formatted amount (e.g., "£100.00", "R2,400.00")
        """
        formatted_amount = f"{amount:,.{decimal_places}f}"

        if include_symbol:
            symbol = self.get_currency_symbol(currency)
            return f"{symbol}{formatted_amount}"

        return formatted_amount

    def get_base_currency(self, user_primary_currency: Optional[str] = None) -> str:
        """
        Get base currency for calculations.

        Args:
            user_primary_currency: User's preferred primary currency

        Returns:
            str: Base currency code (defaults to GBP if not specified)
        """
        if user_primary_currency and user_primary_currency in Currency.__members__:
            return user_primary_currency
        return Currency.GBP.value

    def convert_to_base(
        self,
        amount: float,
        from_currency: str,
        base_currency: str = "GBP"
    ) -> float:
        """
        Convert amount to base currency.

        Args:
            amount: Amount to convert
            from_currency: Source currency
            base_currency: Base currency (default: GBP)

        Returns:
            float: Amount in base currency
        """
        return self.convert_currency(amount, from_currency, base_currency)

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currency codes."""
        return list(Currency.__members__.keys())

    def is_supported_currency(self, currency: str) -> bool:
        """Check if currency is supported."""
        return currency in Currency.__members__


# Global converter instance
currency_converter = CurrencyConverter()


# Convenience functions
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    as_of_date: Optional[date] = None
) -> float:
    """
    Convenience function for currency conversion.

    Example:
        convert_currency(100, "GBP", "ZAR") -> 2400.0
    """
    return currency_converter.convert_currency(amount, from_currency, to_currency, as_of_date)


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Convenience function to get exchange rate.

    Example:
        get_exchange_rate("GBP", "ZAR") -> 24.0
    """
    return currency_converter.get_exchange_rate(from_currency, to_currency)


def format_currency(amount: float, currency: str, decimal_places: int = 2) -> str:
    """
    Convenience function to format currency.

    Example:
        format_currency(100, "GBP") -> "£100.00"
        format_currency(2400, "ZAR") -> "R2,400.00"
    """
    return currency_converter.format_currency(amount, currency, decimal_places=decimal_places)


def get_currency_symbol(currency: str) -> str:
    """
    Convenience function to get currency symbol.

    Example:
        get_currency_symbol("GBP") -> "£"
        get_currency_symbol("ZAR") -> "R"
    """
    return currency_converter.get_currency_symbol(currency)
