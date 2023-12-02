from json import load, dump

source_path = "../configuration/game.json"
destination_path = "../templates/static/database/transactions.json"
backup_path = "../backup/.game_backup.json"


def update(src_path: str, dst_path: str, bkup_path: str):
    # Parse JSON
    data = load(open(src_path, "r"))
    data_2 = load(open(dst_path, "r"))

    # Backup the existing configuration
    dump(data, open(bkup_path, "w"), indent=2)

    # Update the various tables
    for table in data:
        match table:
            case "sources":
                new_name = f"{table[:-1]}_types"
                data_2[new_name] = []

                for item in data[table]:
                    data_2[new_name].append({
                        "name": item,
                        "clean_name": data[table][item]["name"],
                        "description": data[table][item]["description"],
                        "categories": data[table][item]["categories"],
                        "rewards": data[table][item]["rewards"]
                    })
            case "exchanges":
                new_name = f"{table[:-1]}_types"
                data_2[new_name] = []

                for item in data[table]:
                    data_2[new_name].append({
                        "name": item,
                        "clean_name": data[table][item]["name"],
                        "description": data[table][item]["description"],
                        "sources": data[table][item]["sources"],
                        "results": data[table][item]["results"]
                    })
            case "usages":
                new_name = f"{table[:-1]}_types"
                data_2[new_name] = []

                for item in data[table]:
                    data_2[new_name].append({
                        "name": item,
                        "clean_name": data[table][item]["name"],
                        "description": data[table][item]["description"],
                        "item": data[table][item]["item"],
                        "results": data[table][item]["results"]
                    })
            case "materials":
                new_name = f"{table[:-1]}_types"
                data_2[new_name] = []

                for item in data[table]:
                    data_2[new_name].append({
                        "name": item,
                        "clean_name": data[table][item]["name"],
                        "description": data[table][item]["description"],
                        "sources": data[table][item]["sources"],
                        "exchanges": data[table][item]["exchanges"],
                        "exchange_results": data[table][item]["exchange_results"],
                        "usages": data[table][item]["usages"]
                    })
            case _:
                pass

    # Extract unique categories from sources
    categories_set = set()
    for source_key, source_value in data["sources"].items():
        categories_set.update(source_value["categories"])

    # Replace the existing "categories" array
    data["categories"] = {category: {} for category in categories_set}

    # Fill the sources array in the materials using `sources:{}`
    for source in data["sources"]:
        for reward in data["sources"][source]["rewards"]:
            data["materials"].setdefault(reward, {}).setdefault("sources", []).append(source)

    # Convert the updated data back to JSON
    dump(data, open(src_path, "w"), indent=2)
    dump(data_2, open(dst_path, "w"), indent=2)

    return True


if __name__ == '__main__':
    result = update(source_path, destination_path, backup_path)
    print("Updated the configuration successfully." if result else "Failed to update.")
