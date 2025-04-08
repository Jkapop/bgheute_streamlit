import sqlite3
import streamlit as st
from datetime import datetime

# Your existing database connection class
class BGHQueryTool:
    def __init__(self, db_name="bgh_decisions.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row

    def query(self, senat_filter=None, date_filter=None):
        sql = "SELECT * FROM decisions WHERE 1=1"
        params = []

        if senat_filter:
            sql += " AND senat LIKE ?"
            params.append(f"%{senat_filter}%")

        if date_filter:
            if len(date_filter) == 7:
                sql += " AND substr(datum, 1, 7) = ?"
            else:
                sql += " AND datum = ?"
            params.append(date_filter)

        sql += " ORDER BY datum DESC"
        cursor = self.conn.execute(sql, params)
        return cursor.fetchall()

    def close(self):
        self.conn.close()

# Initialize the query tool
tool = BGHQueryTool()

# Streamlit interface
def main():
    st.title("BGH Decision Query Tool")
    st.text("The Database contains BGH decisions from 2019 to 2025.")

    # Sidebar filters
    st.sidebar.header("Filter Options")
    filter_choice = st.sidebar.radio(
        "Select Query Type",
        options=["Filter by Senat Type (Zivil/Straf)", "Get Entries for Specific Senat", 
                 "Get Entries for Specific Date (YYYY-MM-DD)", "Get Entries for Specific Month (YYYY-MM)"]
    )

    # Senat Type filter
    if filter_choice == "Filter by Senat Type (Zivil/Straf)":
        senat_type = st.sidebar.selectbox("Choose Senat Type", ["Zivilsenat", "Strafsenat"])
        if st.sidebar.button("Search"):
            results = tool.query(senat_filter=senat_type)
            display_results(results)

    # Specific Senat filter
    elif filter_choice == "Get Entries for Specific Senat":
        senat = st.sidebar.text_input("Enter exact Senat name (e.g., 'IV. Zivilsenat' or '6. Strafsenat')")
        if st.sidebar.button("Search"):
            results = tool.query(senat_filter=senat)
            display_results(results)

    # Specific Date filter
    elif filter_choice == "Get Entries for Specific Date (YYYY-MM-DD)":
        date = st.sidebar.text_input("Enter date (YYYY-MM-DD)")
        if st.sidebar.button("Search"):
            try:
                datetime.strptime(date, "%Y-%m-%d")  # Validate date format
                results = tool.query(date_filter=date)
                display_results(results)
            except ValueError:
                st.sidebar.error("❌ Invalid date format.")

    # Specific Month filter
    elif filter_choice == "Get Entries for Specific Month (YYYY-MM)":
        month = st.sidebar.text_input("Enter month (YYYY-MM)")
        if st.sidebar.button("Search"):
            try:
                datetime.strptime(month, "%Y-%m")  # Validate month format
                results = tool.query(date_filter=month)
                display_results(results)
            except ValueError:
                st.sidebar.error("❌ Invalid month format.")

# Display results function
def display_results(results):
    if not results:
        st.write("\n❌ No results found.\n")
        return
    st.write(f"\n✅ Found {len(results)} result(s):\n")
    for row in results:
        st.write(f"**Date**: {row['datum']} | **Senat**: {row['senat']} | **Aktenzeichen**: {row['aktenzeichen']} | **Title**: {row['titel']}")
        st.write(f"🔗 [URL]({row['url']})")
        st.write("-" * 80)
    st.write(f"=> Total: {len(results)} results")

# Run the Streamlit app
if __name__ == "__main__":
    main()

    # Close the database connection after app is closed
    tool.close()
