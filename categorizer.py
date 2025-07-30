"""
Smart Expense Categorizer - Transaction Categorization Logic
This module contains the rule-based categorization function for transactions.
"""

import re
from typing import Dict, List

def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on keywords in the description.
    
    Args:
        description (str): Transaction description
        
    Returns:
        str: Category name
    """
    if not description or not isinstance(description, str):
        return "Others"
    
    # Convert to lowercase for case-insensitive matching
    desc_lower = description.lower()
    
    # Define category keywords
    category_keywords = {
        "Food & Dining": [
            "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger", "pizza",
            "food", "dining", "lunch", "dinner", "breakfast", "snack", "grocery",
            "supermarket", "walmart", "target", "costco", "whole foods", "trader joe",
            "domino", "subway", "kfc", "taco bell", "chipotle", "panera", "dunkin",
            "bakery", "deli", "bistro", "grill", "bar", "pub", "kitchen", "eatery"
        ],
        
        "Transportation": [
            "uber", "lyft", "taxi", "gas", "fuel", "parking", "metro", "bus",
            "train", "airline", "flight", "car", "vehicle", "auto", "transport",
            "toll", "subway", "transit", "rental", "hertz", "enterprise", "avis",
            "shell", "exxon", "chevron", "bp", "mobil", "citgo", "speedway"
        ],
        
        "Utilities": [
            "electric", "electricity", "gas", "water", "internet", "phone", "cable",
            "utility", "bill", "energy", "power", "heating", "cooling", "trash",
            "waste", "sewer", "telecom", "verizon", "att", "comcast", "spectrum",
            "xfinity", "cox", "dish", "directv", "netflix", "hulu", "spotify"
        ],
        
        "Shopping": [
            "amazon", "ebay", "store", "shop", "retail", "mall", "outlet", "purchase",
            "buy", "clothing", "clothes", "shoes", "electronics", "home depot",
            "lowes", "best buy", "apple", "microsoft", "nike", "adidas", "zara",
            "h&m", "gap", "old navy", "macys", "nordstrom", "sears", "kohl",
            "tj maxx", "marshall", "ross", "department", "boutique"
        ],
        
        "Entertainment": [
            "movie", "cinema", "theater", "concert", "music", "game", "gaming",
            "entertainment", "fun", "leisure", "hobby", "sport", "gym", "fitness",
            "club", "bar", "nightclub", "casino", "lottery", "ticket", "event",
            "amusement", "park", "zoo", "museum", "gallery", "show", "performance",
            "netflix", "hulu", "disney", "spotify", "youtube", "twitch", "steam"
        ],
        
        "Healthcare": [
            "doctor", "hospital", "medical", "health", "pharmacy", "medicine",
            "dental", "dentist", "clinic", "urgent care", "emergency", "prescription",
            "drug", "cvs", "walgreens", "rite aid", "insurance", "copay", "deductible",
            "therapy", "physical therapy", "mental health", "counseling", "wellness"
        ],
        
        "Income": [
            "salary", "wage", "payroll", "income", "deposit", "payment", "refund",
            "cashback", "bonus", "commission", "dividend", "interest", "transfer",
            "reimbursement", "tax refund", "social security", "pension", "unemployment",
            "freelance", "consulting", "contract", "gig", "tip", "gratuity"
        ],
        
        "Education": [
            "school", "university", "college", "education", "tuition", "book",
            "textbook", "course", "class", "training", "workshop", "seminar",
            "certification", "degree", "diploma", "student", "academic", "learning",
            "library", "research", "study", "exam", "test", "scholarship"
        ],
        
        "Banking": [
            "bank", "atm", "fee", "charge", "overdraft", "maintenance", "service",
            "transfer", "wire", "check", "deposit", "withdrawal", "balance",
            "account", "credit", "debit", "loan", "mortgage", "interest",
            "finance", "investment", "savings", "checking", "penalty"
        ]
    }
    
    # Check each category for keyword matches
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    
    # Special handling for amounts (income detection)
    # If description contains positive indicators and amount context suggests income
    income_indicators = ["deposit", "credit", "payment received", "refund", "cashback"]
    for indicator in income_indicators:
        if indicator in desc_lower:
            return "Income"
    
    # Default category
    return "Others"

def get_category_emoji(category: str) -> str:
    """
    Get emoji for a given category.
    
    Args:
        category (str): Category name
        
    Returns:
        str: Emoji representing the category
    """
    emoji_map = {
        "Food & Dining": "🍔",
        "Transportation": "🚗",
        "Utilities": "🏠",
        "Shopping": "🛍️",
        "Entertainment": "🎬",
        "Healthcare": "🏥",
        "Income": "💰",
        "Education": "📚",
        "Banking": "🏦",
        "Others": "❓"
    }
    
    return emoji_map.get(category, "❓")

def get_category_color(category: str) -> str:
    """
    Get color code for a given category (for visualization).
    
    Args:
        category (str): Category name
        
    Returns:
        str: Hex color code
    """
    color_map = {
        "Food & Dining": "#FF6B6B",
        "Transportation": "#4ECDC4",
        "Utilities": "#45B7D1",
        "Shopping": "#96CEB4",
        "Entertainment": "#FFEAA7",
        "Healthcare": "#DDA0DD",
        "Income": "#98D8C8",
        "Education": "#F7DC6F",
        "Banking": "#BB8FCE",
        "Others": "#AED6F1"
    }
    
    return color_map.get(category, "#AED6F1")

def analyze_spending_patterns(transactions_df) -> Dict:
    """
    Analyze spending patterns from categorized transactions.
    
    Args:
        transactions_df: DataFrame with categorized transactions
        
    Returns:
        Dict: Analysis results
    """
    analysis = {}
    
    # Filter expenses (negative amounts)
    expenses = transactions_df[transactions_df['Amount'] < 0].copy()
    expenses['Amount'] = expenses['Amount'].abs()
    
    if not expenses.empty:
        # Category-wise spending
        category_spending = expenses.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        analysis['top_categories'] = category_spending.head(5).to_dict()
        
        # Average transaction per category
        avg_transaction = expenses.groupby('Category')['Amount'].mean().sort_values(ascending=False)
        analysis['avg_transaction_by_category'] = avg_transaction.to_dict()
        
        # Transaction frequency
        transaction_count = expenses.groupby('Category').size().sort_values(ascending=False)
        analysis['transaction_frequency'] = transaction_count.to_dict()
    
    return analysis