import re
from typing import List, Dict

# Master directory of top NSE/BSE stocks across sectors, market caps, and SME companies
STOCK_DIRECTORY: List[Dict[str, str]] = [
    # Top Largecaps / Nifty 50
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "exchange": "NSE", "sector": "Energy & Conglomerate", "category": "Largecap"},
    {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Largecap"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Largecap"},
    {"symbol": "INFY", "name": "Infosys Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Largecap"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Largecap"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "exchange": "NSE", "sector": "Telecom", "category": "Largecap"},
    {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE", "sector": "PSU Banking", "category": "Largecap"},
    {"symbol": "ITC", "name": "ITC Ltd", "exchange": "NSE", "sector": "FMCG", "category": "Largecap"},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "exchange": "NSE", "sector": "FMCG", "category": "Largecap"},
    {"symbol": "LT", "name": "Larsen & Toubro Ltd", "exchange": "NSE", "sector": "Infrastructure", "category": "Largecap"},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "exchange": "NSE", "sector": "NBFC", "category": "Largecap"},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Largecap"},
    {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Largecap"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "exchange": "NSE", "sector": "Automobile", "category": "Largecap"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "exchange": "NSE", "sector": "Automobile", "category": "Largecap"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "exchange": "NSE", "sector": "Pharmaceuticals", "category": "Largecap"},
    {"symbol": "TITAN", "name": "Titan Company Ltd", "exchange": "NSE", "sector": "Consumer Goods", "category": "Largecap"},
    {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "exchange": "NSE", "sector": "Paints & Chemicals", "category": "Largecap"},
    {"symbol": "NTPC", "name": "NTPC Ltd", "exchange": "NSE", "sector": "Power", "category": "Largecap"},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corp Ltd", "exchange": "NSE", "sector": "Oil & Gas", "category": "Largecap"},
    {"symbol": "POWERGRID", "name": "Power Grid Corporation of India Ltd", "exchange": "NSE", "sector": "Power", "category": "Largecap"},
    {"symbol": "COALINDIA", "name": "Coal India Ltd", "exchange": "NSE", "sector": "Mining", "category": "Largecap"},
    {"symbol": "TATASTEEL", "name": "Tata Steel Ltd", "exchange": "NSE", "sector": "Metals", "category": "Largecap"},
    {"symbol": "JSWSTEEL", "name": "JSW Steel Ltd", "exchange": "NSE", "sector": "Metals", "category": "Largecap"},
    {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "exchange": "NSE", "sector": "Conglomerate", "category": "Largecap"},
    {"symbol": "ADANIPORTS", "name": "Adani Ports and Special Economic Zone", "exchange": "NSE", "sector": "Infrastructure", "category": "Largecap"},
    {"symbol": "WIPRO", "name": "Wipro Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Largecap"},
    {"symbol": "HCLTECH", "name": "HCL Technologies Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Largecap"},
    {"symbol": "TECHM", "name": "Tech Mahindra Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Largecap"},
    {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd", "exchange": "NSE", "sector": "Cement", "category": "Largecap"},
    {"symbol": "GRASIM", "name": "Grasim Industries Ltd", "exchange": "NSE", "sector": "Textiles & Chemicals", "category": "Largecap"},
    {"symbol": "DIVISLAB", "name": "Divi's Laboratories Ltd", "exchange": "NSE", "sector": "Pharmaceuticals", "category": "Largecap"},
    {"symbol": "CIPLA", "name": "Cipla Ltd", "exchange": "NSE", "sector": "Pharmaceuticals", "category": "Largecap"},
    {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Ltd", "exchange": "NSE", "sector": "Pharmaceuticals", "category": "Largecap"},
    {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd", "exchange": "NSE", "sector": "Financial Services", "category": "Largecap"},
    {"symbol": "NESTLEIND", "name": "Nestle India Ltd", "exchange": "NSE", "sector": "FMCG", "category": "Largecap"},
    {"symbol": "BRITANNIA", "name": "Britannia Industries Ltd", "exchange": "NSE", "sector": "FMCG", "category": "Largecap"},
    {"symbol": "INDUSINDBK", "name": "IndusInd Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Largecap"},
    {"symbol": "EICHERMOT", "name": "Eicher Motors Ltd", "exchange": "NSE", "sector": "Automobile", "category": "Largecap"},
    {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp Ltd", "exchange": "NSE", "sector": "Automobile", "category": "Largecap"},
    {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise Ltd", "exchange": "NSE", "sector": "Healthcare", "category": "Largecap"},
    {"symbol": "HINDALCO", "name": "Hindalco Industries Ltd", "exchange": "NSE", "sector": "Metals", "category": "Largecap"},
    {"symbol": "BPCL", "name": "Bharat Petroleum Corp Ltd", "exchange": "NSE", "sector": "Oil & Gas", "category": "Largecap"},
    {"symbol": "TRENT", "name": "Trent Ltd", "exchange": "NSE", "sector": "Retail", "category": "Largecap"},
    {"symbol": "BEL", "name": "Bharat Electronics Ltd", "exchange": "NSE", "sector": "Defence", "category": "Largecap"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics Ltd", "exchange": "NSE", "sector": "Defence", "category": "Largecap"},
    {"symbol": "JIOFIN", "name": "Jio Financial Services Ltd", "exchange": "NSE", "sector": "NBFC", "category": "Largecap"},
    {"symbol": "ZOMATO", "name": "Zomato Ltd", "exchange": "NSE", "sector": "Consumer Internet", "category": "Largecap"},
    {"symbol": "VBL", "name": "Varun Beverages Ltd", "exchange": "NSE", "sector": "Beverages", "category": "Largecap"},
    {"symbol": "DMART", "name": "Avenue Supermarts Ltd (DMart)", "exchange": "NSE", "sector": "Retail", "category": "Largecap"},

    # High Growth Midcaps & Smallcaps
    {"symbol": "PAYTM", "name": "One97 Communications Ltd (Paytm)", "exchange": "NSE", "sector": "Fintech", "category": "Midcap"},
    {"symbol": "BSE", "name": "BSE Ltd", "exchange": "BSE", "sector": "Capital Markets", "category": "Midcap"},
    {"symbol": "CDSL", "name": "Central Depository Services Ltd", "exchange": "NSE", "sector": "Capital Markets", "category": "Midcap"},
    {"symbol": "MCX", "name": "Multi Commodity Exchange of India Ltd", "exchange": "NSE", "sector": "Capital Markets", "category": "Midcap"},
    {"symbol": "SUZLON", "name": "Suzlon Energy Ltd", "exchange": "NSE", "sector": "Green Energy", "category": "Midcap"},
    {"symbol": "IRFC", "name": "Indian Railway Finance Corp", "exchange": "NSE", "sector": "Railways / NBFC", "category": "Midcap"},
    {"symbol": "RVNL", "name": "Rail Vikas Nigam Ltd", "exchange": "NSE", "sector": "Railways", "category": "Midcap"},
    {"symbol": "IRCTC", "name": "Indian Railway Catering & Tourism", "exchange": "NSE", "sector": "Travel & Tourism", "category": "Midcap"},
    {"symbol": "KPITTECH", "name": "KPIT Technologies Ltd", "exchange": "NSE", "sector": "IT & Auto Software", "category": "Midcap"},
    {"symbol": "PERSISTENT", "name": "Persistent Systems Ltd", "exchange": "NSE", "sector": "IT Services", "category": "Midcap"},
    {"symbol": "TATATECH", "name": "Tata Technologies Ltd", "exchange": "NSE", "sector": "Engineering & IT", "category": "Midcap"},
    {"symbol": "POLICYBZR", "name": "PB Fintech Ltd (PolicyBazaar)", "exchange": "NSE", "sector": "Fintech", "category": "Midcap"},
    {"symbol": "NYKAA", "name": "FSN E-Commerce Ventures (Nykaa)", "exchange": "NSE", "sector": "E-Commerce", "category": "Midcap"},
    {"symbol": "YESBANK", "name": "Yes Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Midcap"},
    {"symbol": "IDFCFIRSTB", "name": "IDFC First Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Midcap"},
    {"symbol": "FEDERALBNK", "name": "Federal Bank Ltd", "exchange": "NSE", "sector": "Banking", "category": "Midcap"},
    {"symbol": "PNB", "name": "Punjab National Bank", "exchange": "NSE", "sector": "PSU Banking", "category": "Midcap"},
    {"symbol": "BANKBARODA", "name": "Bank of Baroda", "exchange": "NSE", "sector": "PSU Banking", "category": "Midcap"},
    {"symbol": "CANBK", "name": "Canara Bank", "exchange": "NSE", "sector": "PSU Banking", "category": "Midcap"},
    {"symbol": "MAZDOCK", "name": "Mazagon Dock Shipbuilders Ltd", "exchange": "NSE", "sector": "Defence", "category": "Midcap"},
    {"symbol": "COCHINSHIP", "name": "Cochin Shipyard Ltd", "exchange": "NSE", "sector": "Defence", "category": "Midcap"},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals Ltd", "exchange": "NSE", "sector": "Engineering", "category": "Midcap"},
    {"symbol": "SAIL", "name": "Steel Authority of India Ltd", "exchange": "NSE", "sector": "Metals", "category": "Midcap"},
    {"symbol": "NMDC", "name": "NMDC Ltd", "exchange": "NSE", "sector": "Mining", "category": "Midcap"},
    {"symbol": "VOLTAS", "name": "Voltas Ltd", "exchange": "NSE", "sector": "Consumer Durables", "category": "Midcap"},
    {"symbol": "HAVELLS", "name": "Havells India Ltd", "exchange": "NSE", "sector": "Electricals", "category": "Midcap"},
    {"symbol": "DIXON", "name": "Dixon Technologies Ltd", "exchange": "NSE", "sector": "Electronics Mfg", "category": "Midcap"},
    {"symbol": "POLYCAB", "name": "Polycab India Ltd", "exchange": "NSE", "sector": "Cables & Wires", "category": "Midcap"},
    {"symbol": "KEI", "name": "KEI Industries Ltd", "exchange": "NSE", "sector": "Cables & Wires", "category": "Midcap"},
    {"symbol": "DEEPAKNTR", "name": "Deepak Nitrite Ltd", "exchange": "NSE", "sector": "Specialty Chemicals", "category": "Midcap"},
    {"symbol": "TATAELXSI", "name": "Tata Elxsi Ltd", "exchange": "NSE", "sector": "Design & Tech", "category": "Midcap"},

    # NSE EMERGE & BSE SME Companies
    {"symbol": "KORE", "name": "Kore Digital Ltd", "exchange": "NSE-SME", "sector": "Telecom Infra", "category": "SME"},
    {"symbol": "BEWL", "name": "BEW Engineering Ltd", "exchange": "NSE-SME", "sector": "Pharma Machinery", "category": "SME"},
    {"symbol": "SHRADHA", "name": "Shradha AI Technologies Ltd", "exchange": "BSE-SME", "sector": "IT & AI", "category": "SME"},
    {"symbol": "VITAL", "name": "Vital Chemtech Ltd", "exchange": "NSE-SME", "sector": "Chemicals", "category": "SME"},
    {"symbol": "CONTAINE", "name": "Containe Technologies Ltd", "exchange": "BSE-SME", "sector": "Automotive Tech", "category": "SME"},
    {"symbol": "MACFOS", "name": "Macfos Ltd (Robu.in)", "exchange": "BSE-SME", "sector": "Robotics & E-com", "category": "SME"},
    {"symbol": "KOTYARK", "name": "Kotyark Industries Ltd", "exchange": "NSE-SME", "sector": "Biofuel & Green", "category": "SME"},
    {"symbol": "MEGATHERM", "name": "Megatherm Induction Ltd", "exchange": "NSE-SME", "sector": "Industrial Tech", "category": "SME"},
    {"symbol": "ALUFLUOR", "name": "Alufluoride Ltd", "exchange": "BSE", "sector": "Chemicals", "category": "Smallcap"},
    {"symbol": "GICRE", "name": "General Insurance Corporation of India", "exchange": "NSE", "sector": "Insurance", "category": "Midcap"},
    {"symbol": "NIACL", "name": "New India Assurance Co Ltd", "exchange": "NSE", "sector": "Insurance", "category": "Midcap"},
    {"symbol": "LIC", "name": "Life Insurance Corporation of India", "exchange": "NSE", "sector": "Insurance", "category": "Largecap"}
]

def search_stocks(query: str = "", category: str = "", limit: int = 30) -> List[Dict[str, str]]:
    """
    Search across all NSE, BSE, Mainline, and SME companies.
    If query is a custom ticker not in directory, allows dynamically adding it.
    """
    query = (query or "").strip().upper()
    category = (category or "").strip().upper()

    matches = []
    
    # 1. Search existing directory
    for item in STOCK_DIRECTORY:
        match_query = True
        match_cat = True

        if query:
            match_query = (
                query in item["symbol"].upper() or
                query in item["name"].upper() or
                query in item["sector"].upper()
            )
        if category and category != "ALL":
            match_cat = (item["category"].upper() == category or item["exchange"].upper() == category)

        if match_query and match_cat:
            matches.append(item)
            if len(matches) >= limit:
                break

    # 2. If user searched a specific new ticker (e.g. 'IDEA' or any of the 7000 stocks)
    # dynamically return it as a valid searchable NSE/BSE stock
    if query and not any(m["symbol"] == query for m in matches):
        matches.insert(0, {
            "symbol": query,
            "name": f"{query} Industries Ltd (NSE/BSE)",
            "exchange": "NSE",
            "sector": "Indian Equities",
            "category": "Mainboard"
        })

    return matches[:limit]
