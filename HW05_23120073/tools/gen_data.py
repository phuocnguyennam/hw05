"""Generates the CSV input data for the HW05 workflow.

data/admin_credentials.csv : shared admin account used by every virtual user
                             (only one admin exists in the SUT seed data).
data/products_import.csv   : 500 product rows in the exact template format offered by
                             frontend-admin ("name,price,description,imageUrl,category_id").
                             No commas/quotes inside values because the frontend parser
                             does a naive line.split(",").
"""
import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
random.seed(23120073)  # reproducible

CATALOG = {
    1: (["iPhone", "Samsung Galaxy", "Xiaomi Redmi", "OPPO Reno", "Vivo V", "Realme"],
        ["Điện thoại pin trâu", "Màn hình AMOLED sắc nét", "Camera chụp đêm tốt", "Sạc nhanh 67W"],
        (3_000_000, 35_000_000)),
    2: (["MacBook Air", "Dell XPS", "ASUS ZenBook", "Lenovo ThinkPad", "HP Envy", "Acer Swift"],
        ["Laptop mỏng nhẹ cho văn phòng", "Hiệu năng cao cho lập trình", "Pin dùng cả ngày", "Màn hình 2K"],
        (12_000_000, 60_000_000)),
    3: (["Tai nghe Sony", "Chuột Logitech", "Bàn phím Akko", "Sạc Anker", "Loa JBL", "Ốp lưng Spigen"],
        ["Phụ kiện chính hãng", "Bảo hành 12 tháng", "Thiết kế nhỏ gọn", "Kết nối Bluetooth 5.3"],
        (150_000, 8_000_000)),
}


def main():
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "admin_credentials.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email", "password"])
        w.writerow(["admin@eshop.com", "Admin123!"])

    with open(os.path.join(DATA, "products_import.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["name", "price", "description", "imageUrl", "category_id"])
        for i in range(1, 501):
            cat = random.choice([1, 1, 2, 3, 3])
            brands, descs, (lo, hi) = CATALOG[cat]
            brand = random.choice(brands)
            name = f"{brand} PERF-{i:04d}"
            price = random.randrange(lo, hi, 10_000)
            img = f"https://placehold.co/300x300/png?text=PERF-{i:04d}"
            w.writerow([name, price, random.choice(descs), img, cat])
    print("CSV data written to", os.path.normpath(DATA))


if __name__ == "__main__":
    main()
