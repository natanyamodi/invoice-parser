from dotenv import load_dotenv
load_dotenv()  

import streamlit as st
from agno.agent import Agent 
from agno.media import Image
from agno.models.google import Gemini 
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd

st.set_page_config(
    page_title="Invoice Parsing",
    layout="wide",
)

class Item(BaseModel):
    item_name: str = Field(..., description="The name of the item")
    quantity: int = Field(..., description="The quantity of the item")
    unit_price: float = Field(..., description="The unit price of the item")
    total_price: float = Field(..., description="The total price of the item")
    description: Optional[str] = Field(None, description="Description of the item")

class Customer(BaseModel):
    name: str = Field(..., description="The name of the customer")
    address: str = Field(..., description="The address of the customer")
    phone_number: Optional[str] = Field(None, description="The phone number of the customer")
    email: Optional[str] = Field(None, description="The email of the customer")

class Invoice(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    company_address: str = Field(..., description="The address of the company")
    invoice_number: str = Field(..., description="The invoice number")
    invoice_date: Optional[str] = Field(None, description="The date of the invoice")
    bill_to: str = Field(..., description="The name of the person and address to bill to")
    ship_to: Optional[str] = Field(None, description="The name of the person and address to ship to")
    sub_total: float = Field(..., description="The subtotal amount of the invoice")
    tax: float = Field(..., description="The tax amount")
    total_amount: float = Field(..., description="The total amount of the invoice")
    due_date: Optional[str] = Field(None, description="Due date for payment")
    items: List[Item] = Field(..., description="List of items in the invoice")
    customer: Customer = Field(..., description="Customer information")

def parse_invoice(uploaded_file):
    # Read the file content
    file_bytes = uploaded_file.read()
    
    # Create Agno Image object using content parameter
    agno_image = Image(content=file_bytes)
    
    agent = Agent(
        model=Gemini("gemini-2.0-flash"),
        description="Parse the invoices and extract the relevant information including items and customer details.",
        response_model=Invoice,
    )
    
    response = agent.run(
        "Extract all invoice information from this image including items and customer details",
        images=[agno_image],
        stream=True
    )

    return response.content

def main():
    # Initialize session state variables if they don't exist
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = []
        st.session_state.invoices_df = pd.DataFrame()
        st.session_state.items_df = pd.DataFrame()
        st.session_state.customers_df = pd.DataFrame()
        st.session_state.show_results = True

    st.title("Invoice Parsing")

    uploaded_files = st.file_uploader(
        "Upload your invoice files", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )

    if st.button("🎯 Parse Invoices", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing invoices..."):
                st.session_state.parsed_data = []
                st.session_state.invoices_df = pd.DataFrame()
                st.session_state.items_df = pd.DataFrame()
                st.session_state.customers_df = pd.DataFrame()
                
                new_data = []
                for file in uploaded_files:
                    try:
                        st.write(f"Processing file: {file.name}")
                        
                        # Parse the invoice
                        parsed_data = parse_invoice(file)
                        
                        # Convert to dictionary and store results
                        parsed_dict = parsed_data.model_dump()
                        parsed_dict['filename'] = file.name  # Add filename to the data
                        new_data.append(parsed_dict)
                        
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                        continue
                
                if new_data:
                    st.session_state.parsed_data = new_data
                    
                    # Create fresh DataFrames for each tab
                    invoices_data = []
                    items_data = []
                    customers_data = []
                    
                    for invoice in st.session_state.parsed_data:
                        # Prepare invoice data (excluding items and customer)
                        invoice_data = {k: v for k, v in invoice.items() 
                                      if k not in ['items', 'customer']}
                        invoices_data.append(invoice_data)
                        
                        # Prepare items data
                        for item in invoice['items']:
                            item_data = item.copy()
                            item_data['invoice_number'] = invoice['invoice_number']
                            item_data['filename'] = invoice['filename']
                            items_data.append(item_data)
                        
                        # Prepare customer data
                        customer_data = invoice['customer'].copy()
                        customer_data['invoice_number'] = invoice['invoice_number']
                        customer_data['filename'] = invoice['filename']
                        customers_data.append(customer_data)
                    
                    # Create new DataFrames
                    st.session_state.invoices_df = pd.DataFrame(invoices_data)
                    st.session_state.items_df = pd.DataFrame(items_data)
                    st.session_state.customers_df = pd.DataFrame(customers_data)
                    
                    st.session_state.show_results = True
                    st.success(f"Successfully processed {len(new_data)} invoices!")
                else:
                    st.session_state.show_results = False
    
    # Display tabs if we have data and results should be shown
    if st.session_state.show_results and not st.session_state.invoices_df.empty:
        tab1, tab2, tab3 = st.tabs(["Invoices", "Items", "Customers"])
        
        with tab1:
            st.subheader("Parsed Invoices")
            st.dataframe(st.session_state.invoices_df)
            
        with tab2:
            st.subheader("Invoice Items")
            st.dataframe(st.session_state.items_df)
            
        with tab3:
            st.subheader("Customers")
            st.dataframe(st.session_state.customers_df)

if __name__ == "__main__":
    main()