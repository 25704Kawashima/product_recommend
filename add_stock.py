import pandas as pd
import random

# CSVファイルの読み込み
csv_file_path = "/Users/hswuser/Documents/kawashima/product_recommend/data/products.csv"
df = pd.read_csv(csv_file_path)

# ランダムに「あり」「残りわずか」「なし」を割り振る
stock_status_options = ["あり", "残りわずか", "なし"]
df["stock_status"] = [random.choice(stock_status_options) for _ in range(len(df))]

# CSVファイルの保存
output_file_path = "/Users/hswuser/Documents/kawashima/product_recommend/data/products_with_stock_status.csv"
df.to_csv(output_file_path, index=False, encoding="utf-8-sig")

print(f"新しいCSVファイルが保存されました: {output_file_path}")