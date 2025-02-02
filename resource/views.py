from django.shortcuts import render
from resource.models import SKUDetailFile, SKUPriceFile
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

#  Sales forecasts will be computed using predefined percentage increases per SKU.
#  Example increase percentage data:
SALES_INCREASE = {
    "A": 10,
    "B": 7.5,
    "C": 8,
    "D": 12
}

def upload_files(request):
    if request.method == "POST":
        sku_price_file = request.FILES.get("sku_price_file")
        sku_detail_file = request.FILES.get("sku_detail_file")
        if SKUPriceFile.objects.filter(filename=sku_price_file.name).exists():
            return render(request,"index.html", {"error_message": "This SKU Price File already exists!"})
        if SKUDetailFile.objects.filter(filename=sku_detail_file.name).exists():
            return render(request,"index.html", {"error_message": "This SKU Detail File already exists!"})
        SKUPriceFile.objects.create(
            file=sku_price_file,
            filename=sku_price_file.name
        )
        SKUDetailFile.objects.create(
            file=sku_detail_file,
            filename=sku_detail_file.name
        )
        fl1 = pd.read_excel(sku_price_file)
        fl2 = pd.read_excel(sku_detail_file)
        allfile = pd.merge(fl1, fl2, on='SKUs')
        if "Current stocks" in allfile.columns:
           allfile.drop(columns=["Current stocks"], inplace=True)
        allfile["Sales Forecast"] = allfile["Last month sales"] + (allfile["Last month sales"] * allfile["SKUs"].map(SALES_INCREASE) / 100)
        allfile["Purchase Order (PO)"] = allfile["Sales Forecast"] * allfile["Price"]
        if "Last month sales" in allfile.columns:
           allfile.drop(columns=["Last month sales"], inplace=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            allfile.to_excel(writer, index=False)
        output.seek(0)

        # Create response with the Excel file
        response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=output.xlsx"

        return response

    return render(request, "index.html")