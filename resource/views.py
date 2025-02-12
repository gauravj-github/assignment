from django.shortcuts import render
from resource.models import SKUDetailFile, SKUPriceFile
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
import matplotlib.pyplot as plt
import base64

# Sales forecasts will be computed using predefined percentage increases per SKU.
SALES_INCREASE = {
    "A": 10,
    "B": 7.5,
    "C": 8,
    "D": 12
}

def upload_files(request):
    chart = None  
    file_available = False  
    if request.method == "POST":
        sku_price_file = request.FILES.get("sku_price_file")
        sku_detail_file = request.FILES.get("sku_detail_file")

        if SKUPriceFile.objects.filter(filename=sku_price_file.name).exists():
            return render(request, "index.html", {"error_message": "This SKU Price File already exists!"})

        if SKUDetailFile.objects.filter(filename=sku_detail_file.name).exists():
            return render(request, "index.html", {"error_message": "This SKU Detail File already exists!"})

        SKUPriceFile.objects.create(file=sku_price_file, filename=sku_price_file.name)
        SKUDetailFile.objects.create(file=sku_detail_file, filename=sku_detail_file.name)

        fl1 = pd.read_excel(sku_price_file)
        fl2 = pd.read_excel(sku_detail_file)

        allfile = pd.merge(fl1, fl2, on="SKUs")

        if "Current stocks" in allfile.columns:
            allfile.drop(columns=["Current stocks"], inplace=True)

        allfile["Sales Forecast"] = allfile["Last month sales"] + (allfile["Last month sales"] * allfile["SKUs"].map(SALES_INCREASE) / 100)

        allfile["Purchase Order (PO)"] = allfile["Sales Forecast"] * allfile["Price"]

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            allfile.to_excel(writer, index=False)
        output.seek(0)

        if "Last month sales" in allfile.columns:
            last_month_sales = allfile["Last month sales"]
            sales_forecast = allfile["Sales Forecast"]
            sku_labels = allfile["SKUs"]

            plt.figure(figsize=(10, 5))
            plt.plot(sku_labels, last_month_sales, marker="o", label="Last Month Sales", linestyle="-", color="blue")
            plt.plot(sku_labels, sales_forecast, marker="s", label="Sales Forecast", linestyle="--", color="red")
            plt.xlabel("SKU")
            plt.ylabel("Sales")
            plt.title("Last Month Sales vs Sales Forecast")
            plt.legend()
            plt.grid()

            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            chart = f"data:image/png;base64,{image_base64}"

        request.session["excel_file"] = output.getvalue().decode("latin1")
        file_available = True

        return render(request, "index.html", {"chart": chart, "file_available": file_available})

    return render(request, "index.html")


def download_file(request):
    """Handle file download separately"""
    excel_file = request.session.get("excel_file")
    if not excel_file:
        return HttpResponse("No file available", status=404)

    response = HttpResponse(excel_file.encode("latin1"), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=output.xlsx"
    return response
