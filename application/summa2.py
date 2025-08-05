import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import webbrowser

# Step 1: Mock the MySQL query result
def execute_mysql_query(query):
    return {
        "results": [
            {"product": "Apple", "sales": 120},
            {"product": "Banana", "sales": 80},
            {"product": "Orange", "sales": 100},
            {"product": "Mango", "sales": 150}
        ]
    }

# Step 2: Generate the chart
def generate_chart(data, chart_type="bar"):
    df = pd.DataFrame(data["results"])

    # Create plot
    fig, ax = plt.subplots()
    df.plot(kind=chart_type, x="product", y="sales", ax=ax, color="#200695")

    # Save chart to file
    output_dir = "charts"
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(output_dir, file_name)

    fig.savefig(file_path)
    plt.close(fig)

    print(f"✅ Chart saved to {file_path}")

    # Open the image in the default image viewer
    webbrowser.open(f"file://{os.path.abspath(file_path)}")

# Step 3: Run everything
if __name__ == "__main__":
    query = "SELECT product, sales FROM sales_data"
    table = execute_mysql_query(query)
    generate_chart(table, chart_type="bar")
