# 🍽️ Restaurant Insights: NoSQL Analytics Dashboard

An interactive Streamlit dashboard on top of a MongoDB restaurant ordering and review database. It reads nine document collections and turns them into filterable KPIs and Plotly charts covering orders, revenue, restaurant performance, customer ratings and menu pricing.

## Stack

`Python` · `Streamlit` · `MongoDB` (`pymongo`) · `pandas` · `NumPy` · `Plotly`

## What it does

- Connects to MongoDB (`restaurante_reviews_db`) and loads the orders, restaurants, dishes, menus, reviews, users, messages, notifications and reports collections, with a 10-minute cache.
- Sidebar filters by restaurant category, date range, restaurant and order status.
- KPI cards for total orders, total revenue, delivery success rate and average ticket.
- Order analysis: status distribution, orders by day of week, and orders vs revenue over time.
- Restaurant and rating analysis: top 10 restaurants by revenue, revenue by cuisine type, rating distribution and monthly average rating.
- Menu analysis: dish price distribution and the 10 most expensive dishes.

## How to run

```bash
pip install -r requirements.txt

# MongoDB connection string, read via st.secrets
mkdir -p .streamlit
echo 'MONGODB_URI = "mongodb://localhost:27017"' > .streamlit/secrets.toml

streamlit run app.py
```

The app expects a MongoDB database named `restaurante_reviews_db` populated with the collections listed above. A hosted version was published at https://dash-restaurante.streamlit.app.

## Credits

Group project originally by [felipe-teodoro-bandeira](https://github.com/felipe-teodoro-bandeira) ([felipe-teodoro-bandeira/dashboard-restaurante-NoSQL](https://github.com/felipe-teodoro-bandeira/dashboard-restaurante-NoSQL)), built with Lucas Wall, João Vitor and Mateo Wall; Lucas Wall as contributor. Licensed under MIT (see [LICENSE](LICENSE)).
