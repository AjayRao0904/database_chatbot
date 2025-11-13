# Olist Dataset Structure & Schema Reference

## 📊 Dataset Overview

**Source:** Brazilian E-Commerce Public Dataset by Olist  
**Period:** 2016-2018  
**Records:** ~100,000 orders  
**Language:** Portuguese (Brazilian)  
**Format:** 9 relational CSV files

## 🗂️ File Descriptions

### 1. `olist_customers_dataset.csv`
**Purpose:** Customer information and location  
**Size:** ~9 MB | ~99,441 rows

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | VARCHAR(255) | Unique customer ID for each order (PK) |
| `customer_unique_id` | VARCHAR(255) | Actual unique customer ID (for tracking repeat customers) |
| `customer_zip_code_prefix` | VARCHAR(10) | First 5 digits of customer zip code |
| `customer_city` | VARCHAR(255) | Customer city name |
| `customer_state` | VARCHAR(10) | Customer state (2-letter code) |

**Note:** Same customer gets different `customer_id` for different orders. Use `customer_unique_id` to identify repeat customers.

---

### 2. `olist_sellers_dataset.csv`
**Purpose:** Seller information and location

| Column | Type | Description |
|--------|------|-------------|
| `seller_id` | VARCHAR(255) | Unique seller ID (PK) |
| `seller_zip_code_prefix` | VARCHAR(10) | First 5 digits of seller zip code |
| `seller_city` | VARCHAR(255) | Seller city name |
| `seller_state` | VARCHAR(10) | Seller state (2-letter code) |

---

### 3. `olist_products_dataset.csv`
**Purpose:** Product information and dimensions

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | VARCHAR(255) | Unique product ID (PK) |
| `product_category_name` | VARCHAR(255) | Product category (in Portuguese) |
| `product_name_length` | INTEGER | Character count of product name |
| `product_description_length` | INTEGER | Character count of product description |
| `product_photos_qty` | INTEGER | Number of product photos |
| `product_weight_g` | INTEGER | Product weight in grams |
| `product_length_cm` | INTEGER | Product length in cm |
| `product_height_cm` | INTEGER | Product height in cm |
| `product_width_cm` | INTEGER | Product width in cm |

---

### 4. `product_category_name_translation.csv`
**Purpose:** Translate Portuguese category names to English

| Column | Type | Description |
|--------|------|-------------|
| `product_category_name` | VARCHAR(255) | Category name in Portuguese (PK) |
| `product_category_name_english` | VARCHAR(255) | Category name in English |

**Categories:** 71 unique categories (e.g., "beleza_saude" → "health_beauty")

---

### 5. `olist_orders_dataset.csv`
**Purpose:** Order status and timestamps

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | VARCHAR(255) | Unique order ID (PK) |
| `customer_id` | VARCHAR(255) | Customer ID (FK) |
| `order_status` | VARCHAR(50) | Order status (delivered, shipped, etc.) |
| `order_purchase_timestamp` | TIMESTAMP | Purchase timestamp |
| `order_approved_at` | TIMESTAMP | Payment approval timestamp |
| `order_delivered_carrier_date` | TIMESTAMP | Order handed to carrier |
| `order_delivered_customer_date` | TIMESTAMP | Actual delivery to customer |
| `order_estimated_delivery_date` | TIMESTAMP | Estimated delivery date |

**Order Statuses:**
- `delivered` - Order delivered
- `shipped` - Order shipped
- `processing` - Being processed
- `canceled` - Canceled
- `unavailable` - Product unavailable
- `invoiced` - Invoice issued
- `created` - Order created
- `approved` - Payment approved

---

### 6. `olist_order_items_dataset.csv`
**Purpose:** Items within each order (one order can have multiple items)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | VARCHAR(255) | Order ID (FK) |
| `order_item_id` | INTEGER | Item sequence number within order |
| `product_id` | VARCHAR(255) | Product ID (FK) |
| `seller_id` | VARCHAR(255) | Seller ID (FK) |
| `shipping_limit_date` | TIMESTAMP | Shipping deadline |
| `price` | DECIMAL(10,2) | Item price |
| `freight_value` | DECIMAL(10,2) | Freight/shipping cost |

**Key Insights:**
- One order can have multiple items
- Each item may be from different sellers
- Total order value = SUM(price) + SUM(freight_value)

---

### 7. `olist_order_payments_dataset.csv`
**Purpose:** Payment information (one order can have multiple payment methods)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | VARCHAR(255) | Order ID (FK) |
| `payment_sequential` | INTEGER | Sequential number for multi-payment orders |
| `payment_type` | VARCHAR(50) | Payment method |
| `payment_installments` | INTEGER | Number of installments |
| `payment_value` | DECIMAL(10,2) | Payment value |

**Payment Types:**
- `credit_card` - Credit card
- `boleto` - Brazilian payment method (cash/bank transfer)
- `voucher` - Gift voucher
- `debit_card` - Debit card

---

### 8. `olist_order_reviews_dataset.csv`
**Purpose:** Customer reviews and ratings

| Column | Type | Description |
|--------|------|-------------|
| `review_id` | VARCHAR(255) | Unique review ID (PK) |
| `order_id` | VARCHAR(255) | Order ID (FK) |
| `review_score` | INTEGER | Rating (1-5 stars) |
| `review_comment_title` | TEXT | Review title |
| `review_comment_message` | TEXT | Review text (in Portuguese) |
| `review_creation_date` | TIMESTAMP | Review creation date |
| `review_answer_timestamp` | TIMESTAMP | Review answer timestamp |

**Score Distribution:**
- 5 stars: ~58%
- 4 stars: ~19%
- 3 stars: ~8%
- 2 stars: ~3%
- 1 star: ~12%

---

### 9. `olist_geolocation_dataset.csv`
**Purpose:** Brazilian zip codes with lat/lng coordinates

| Column | Type | Description |
|--------|------|-------------|
| `geolocation_zip_code_prefix` | VARCHAR(10) | Zip code prefix (5 digits) |
| `geolocation_lat` | DECIMAL(10,8) | Latitude |
| `geolocation_lng` | DECIMAL(11,8) | Longitude |
| `geolocation_city` | VARCHAR(255) | City name |
| `geolocation_state` | VARCHAR(10) | State code |

**Note:** Original file has ~1M rows with duplicates. We deduplicate on zip_code_prefix.

---

## 🔗 Entity Relationship Diagram

```
┌─────────────────┐
│   CUSTOMERS     │
│─────────────────│
│ customer_id (PK)│─┐
│ customer_unique │ │
│ zip_code       │ │
│ city           │ │
│ state          │ │
└─────────────────┘ │
                    │
                    │ 1:N
                    ▼
┌─────────────────┐
│     ORDERS      │
│─────────────────│
│ order_id (PK)   │─┬─────────────────┐
│ customer_id (FK)│ │                 │
│ order_status    │ │                 │
│ purchase_time   │ │                 │
│ delivery_time   │ │                 │
└─────────────────┘ │                 │
                    │ 1:N             │ 1:N
                    ▼                 ▼
┌─────────────────┐         ┌─────────────────┐
│  ORDER_ITEMS    │         │ ORDER_PAYMENTS  │
│─────────────────│         │─────────────────│
│ order_id (FK)   │         │ order_id (FK)   │
│ product_id (FK) │─┐       │ payment_type    │
│ seller_id (FK)  │ │       │ payment_value   │
│ price           │ │       │ installments    │
│ freight_value   │ │       └─────────────────┘
└─────────────────┘ │
                    │              1:N
                    │               ▼
┌─────────────────┐ │      ┌─────────────────┐
│    PRODUCTS     │ │      │ ORDER_REVIEWS   │
│─────────────────│ │      │─────────────────│
│ product_id (PK) │◄┘      │ review_id (PK)  │
│ category_name   │─┐      │ order_id (FK)   │
│ weight_g        │ │      │ review_score    │
│ dimensions      │ │      │ comment         │
└─────────────────┘ │      └─────────────────┘
                    │
                    │ N:1
                    ▼
┌─────────────────────────┐
│ CATEGORY_TRANSLATION    │
│─────────────────────────│
│ category_name_pt (PK)   │
│ category_name_en        │
└─────────────────────────┘

┌─────────────────┐
│    SELLERS      │
│─────────────────│
│ seller_id (PK)  │◄─┐
│ zip_code        │  │
│ city            │  │
│ state           │  │
└─────────────────┘  │
                     │
        ┌────────────┘
        │ N:1
        │
    (from ORDER_ITEMS)
```

---

## 📈 Key Statistics (Approximate)

| Metric | Value |
|--------|-------|
| Total Orders | ~100,000 |
| Unique Customers | ~96,000 |
| Repeat Customers | ~3,000 (3%) |
| Products | ~32,000 |
| Sellers | ~3,000 |
| Categories | 71 |
| Order Items | ~112,000 |
| Reviews | ~99,000 |
| Date Range | Sept 2016 - Aug 2018 |
| States Covered | 27 (all Brazilian states) |
| Cities | ~4,000 |

---

## 🔍 Common Join Patterns

### Get full order details with customer info:
```sql
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
LEFT JOIN order_reviews r ON o.order_id = r.order_id
```

### Get order with payment info:
```sql
FROM orders o
JOIN order_payments op ON o.order_id = op.order_id
```

### Get seller performance:
```sql
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
```

---

## 💡 Agent Analysis Opportunities

### Self-Correcting SQL Agent
- Parse complex questions into SQL
- Handle Portuguese category names
- Join across multiple tables
- Aggregate sales, reviews, delivery metrics

### Hypothesis Generation Agent
**Example:** "Why are electronics sales low in São Paulo?"
- Check delivery performance in São Paulo
- Compare review scores across regions
- Analyze price competitiveness
- Check seller availability

### Proactive Insight Agent
**After showing sales data:**
- "I noticed 85% of Product X sales occur with Product Y"
- "Delivery times in State Z are 40% longer than average"
- "Category A has high sales but low review scores"

### External Knowledge Agent
- Search for product reviews online
- Find competitor pricing
- Get regional economic data
- Understand Brazilian holidays/events

---

## 🌍 Geographic Notes

**Brazilian States (27):**
- SP (São Paulo) - Largest economic hub
- RJ (Rio de Janeiro) - Second largest
- MG (Minas Gerais) - Third largest
- And 24 others

**Timezone:** Most of Brazil is UTC-3  
**Language:** Portuguese (Brazilian)
