import gspread
from google.oauth2.service_account import Credentials

# ============================================
# INVENTORY MANAGEMENT SYSTEM
# Built by: Adnan
# Purpose: Automate inventory tracking and alerts
# ============================================

print("=" * 60)
print("        📦 INVENTORY MANAGEMENT SYSTEM")
print("=" * 60)

# ============================================
# SECTION 1: SETUP & CONNECTION
# ============================================

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    creds = Credentials.from_service_account_file('credentials.json (2).json', scopes=scopes)
    client = gspread.authorize(creds)
    print("✅ Connected to Google Sheets")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

try:
    spreadsheet = client.open("Inventory Master")
    sheet = spreadsheet.sheet1
    print("✅ Opened Inventory Master sheet")
except Exception as e:
    print(f"❌ Could not open sheet: {e}")
    exit()

try:
    products = sheet.get_all_records()
    
    if len(products) == 0:
        print("❌ No products found in sheet!")
        exit()
    
    print(f"✅ Loaded {len(products)} products\n")
except Exception as e:
    print(f"❌ Error reading data: {e}")
    exit()

# ============================================
# SECTION 2: ANALYZE LOW STOCK ITEMS
# ============================================

print("=" * 60)
print("        ⚠️  LOW STOCK ANALYSIS")
print("=" * 60 + "\n")

low_stock_items = []
total_reorder_cost = 0

for product in products:
    if product['Stock'] < product['Reorder_pt']:
        units_to_order = product['Reorder_pt'] - product['Stock']
        reorder_cost = units_to_order * product['Price']
        
        low_stock_item = {
            'Product': product['Product'],
            'Price': product['Price'],
            'Current_Stock': product['Stock'],
            'Reorder_pt': product['Reorder_pt'],
            'Units_Needed': units_to_order,
            'Reorder_Cost': reorder_cost,
            'Category': product['Category']
        }
        
        low_stock_items.append(low_stock_item)
        total_reorder_cost += reorder_cost
        
        print(f"• {product['Product']}: Stock {product['Stock']} / Reorder at {product['Reorder_pt']} → Order {units_to_order} units (${reorder_cost:,})")

print(f"\n📊 Total items needing restock: {len(low_stock_items)}")
print(f"💰 Total reorder cost: ${total_reorder_cost:,}\n")

if len(low_stock_items) == 0:
    print("✅ All products are well-stocked!")
    exit()

# ============================================
# SECTION 3: CREATE LOW STOCK ALERTS SHEET
# ============================================

print("=" * 60)
print("        📋 CREATING ALERTS SHEET")
print("=" * 60 + "\n")

try:
    alerts_sheet = spreadsheet.worksheet("Low Stock Alerts")
    alerts_sheet.clear()
    print("✅ Cleared existing Alerts sheet")
except:
    alerts_sheet = spreadsheet.add_worksheet(
        title="Low Stock Alerts",
        rows=100,
        cols=6
    )
    print("✅ Created new Alerts sheet")

# Write headers - BOLD ONLY, NO COLORS
headers = [['Product', 'Current Stock', 'Reorder Point', 'Units Needed', 'Reorder Cost', 'Category']]
alerts_sheet.update('A1:F1', headers)

# Format headers - BOLD ONLY
alerts_sheet.format('A1:F1', {
    "textFormat": {"bold": True, "fontSize": 11}
})

# Write low stock items
row_num = 2
for item in low_stock_items:
    row_data = [[
        item['Product'],
        item['Current_Stock'],
        item['Reorder_pt'],
        item['Units_Needed'],
        f"${item['Reorder_Cost']:,}",
        item['Category']
    ]]
    
    alerts_sheet.update(f'A{row_num}:F{row_num}', row_data)
    row_num += 1

print(f"✅ Wrote {len(low_stock_items)} items to Alerts sheet")

# ============================================
# SECTION 4: CREATE SUMMARY DASHBOARD
# ============================================

print("\n" + "=" * 60)
print("        📊 CREATING SUMMARY DASHBOARD")
print("=" * 60 + "\n")

try:
    summary_sheet = spreadsheet.worksheet("Summary Dashboard")
    summary_sheet.clear()
    print("✅ Cleared existing Summary sheet")
except:
    summary_sheet = spreadsheet.add_worksheet(
        title="Summary Dashboard",
        rows=50,
        cols=2
    )
    print("✅ Created new Summary sheet")

# Write headers - BOLD ONLY
summary_sheet.update('A1:B1', [['Metric', 'Value']])
summary_sheet.format('A1:B1', {
    "textFormat": {"bold": True, "fontSize": 11}
})

# Calculate statistics
total_products = len(products)
low_stock_count = len(low_stock_items)
good_stock_count = total_products - low_stock_count
total_inventory_value = sum(p['Price'] * p['Stock'] for p in products)

most_critical = min(low_stock_items, key=lambda x: x['Current_Stock'] / x['Reorder_pt'])

category_counts = {}
for item in low_stock_items:
    cat = item['Category']
    if cat in category_counts:
        category_counts[cat] += 1
    else:
        category_counts[cat] = 1

most_affected_category = max(category_counts, key=category_counts.get)

# Write summary data - NO COLORS
summary_data = [
    ['Total Products', total_products],
    ['Low Stock Items', low_stock_count],
    ['Items in Good Stock', good_stock_count],
    ['Total Inventory Value', f'${total_inventory_value:,}'],
    ['Total Reorder Cost', f'${total_reorder_cost:,}'],
    ['Most Critical Product', f"{most_critical['Product']} (only {most_critical['Current_Stock']} left)"],
    ['Category Most Affected', f"{most_affected_category} ({category_counts[most_affected_category]} items)"]
]

summary_sheet.update('A2:B8', summary_data)

print("✅ Summary dashboard created")

# ============================================
# SECTION 5: FINAL REPORT
# ============================================

print("\n" + "=" * 60)
print("        ✅ SYSTEM COMPLETE")
print("=" * 60)

print(f"""
📊 INVENTORY ANALYSIS SUMMARY:
   
   Total Products Tracked:     {total_products}
   Low Stock Items:            {low_stock_count}
   Items in Good Stock:        {good_stock_count}
   
   💰 Financial Impact:
   Total Inventory Value:      ${total_inventory_value:,}
   Total Reorder Cost:         ${total_reorder_cost:,}
   
   ⚠️  Most Critical:
   {most_critical['Product']} (only {most_critical['Current_Stock']} left, need {most_critical['Units_Needed']} units)
   
   📋 Reports Created:
   ✅ Low Stock Alerts sheet
   ✅ Summary Dashboard sheet
""")

print("=" * 60)
print("     🎉 Check your Google Sheets now!")
print("=" * 60)