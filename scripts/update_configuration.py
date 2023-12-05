from json import load, dump

source_path = "../configuration/game.json"
destination_path = "../templates/static/database/transactions.json"
index_path = "../templates/static/database/index.json"
backup_path = "../backup/game.json.bak"
backup_2_path = "../backup/transactions.json.bak"


def update(src_path: str, dst_path: str, inx_path: str, bkup_path: str, bkup_2_path: str):
    # Parse JSON
    game_json = load(open(src_path, "r"))
    transactions_json = load(open(dst_path, "r"))
    index_json = load(open(inx_path, "r"))

    # Backup the existing configuration
    dump(game_json, open(bkup_path, "w"), indent=2)
    dump(transactions_json, open(bkup_2_path, "w"), indent=2)

    # Update the various tables
    for table in game_json:
        match table:
            case "sources":
                new_name = f"{table[:-1]}_types"
                transactions_json[new_name] = []

                for item in game_json[table]:
                    new_uuid = next((item_1["uuid"] for item_1 in index_json["uuid_index"]
                                     if item_1["table_name"] == new_name and
                                     item_1["uuid"] not in str(transactions_json[new_name])), None)

                    if not new_uuid:
                        raise Exception("Could not find UUID for sources")

                    transactions_json[new_name].append({
                        "uuid": new_uuid,
                        "name": item,
                        "clean_name": game_json[table][item]["name"],
                        "description": game_json[table][item]["description"],
                        "categories": game_json[table][item]["categories"],
                        "rewards": game_json[table][item]["rewards"]
                    })
            case "exchanges":
                new_name = f"{table[:-1]}_types"
                transactions_json[new_name] = []

                for item in game_json[table]:
                    new_uuid = next((item_1["uuid"] for item_1 in index_json["uuid_index"]
                                     if item_1["table_name"] == new_name and
                                     item_1["uuid"] not in str(transactions_json[new_name])), None)

                    if not new_uuid:
                        raise Exception("Could not find UUID for sources")

                    transactions_json[new_name].append({
                        "uuid": new_uuid,
                        "name": item,
                        "clean_name": game_json[table][item]["name"],
                        "description": game_json[table][item]["description"],
                        "sources": game_json[table][item]["sources"],
                        "results": game_json[table][item]["results"]
                    })
            case "usages":
                new_name = f"{table[:-1]}_types"
                transactions_json[new_name] = []

                for item in game_json[table]:
                    new_uuid = next((item_1["uuid"] for item_1 in index_json["uuid_index"]
                                     if item_1["table_name"] == new_name and
                                     item_1["uuid"] not in str(transactions_json[new_name])), None)

                    if not new_uuid:
                        raise Exception("Could not find UUID for sources")

                    transactions_json[new_name].append({
                        "uuid": new_uuid,
                        "name": item,
                        "clean_name": game_json[table][item]["name"],
                        "description": game_json[table][item]["description"],
                        "item": game_json[table][item]["item"],
                        "results": game_json[table][item]["results"]
                    })
            case "materials":
                new_name = f"{table[:-1]}_types"
                transactions_json[new_name] = []

                for item in game_json[table]:
                    new_uuid = next((item_1["uuid"] for item_1 in index_json["uuid_index"]
                                     if item_1["table_name"] == new_name and
                                     item_1["uuid"] not in str(transactions_json[new_name])), None)

                    if not new_uuid:
                        raise Exception("Could not find UUID for sources")

                    transactions_json[new_name].append({
                        "uuid": new_uuid,
                        "name": item,
                        "clean_name": game_json[table][item]["name"],
                        "description": game_json[table][item]["description"],
                        "sources": game_json[table][item]["sources"],
                        "exchanges": game_json[table][item]["exchanges"],
                        "exchange_results": game_json[table][item]["exchange_results"],
                        "usages": game_json[table][item]["usages"]
                    })
            case _:
                pass

    # Extract unique categories from sources
    categories_set = set()
    for source_key, source_value in game_json["sources"].items():
        categories_set.update(source_value["categories"])

    # Replace the existing "categories" array
    game_json["categories"] = {category: {} for category in categories_set}

    # Reset the sources array for each material
    for material in game_json["materials"]:
        game_json["materials"][material]["sources"] = []

    # Fill the sources array in the materials using `sources:{}`
    for source in game_json["sources"]:
        for reward in game_json["sources"][source]["rewards"]:
            game_json["materials"].setdefault(reward, {}).setdefault("sources", []).append(source)

    # Convert the updated data back to JSON
    dump(game_json, open(src_path, "w"), indent=2)
    dump(transactions_json, open(dst_path, "w"), indent=2)

    return True


if __name__ == '__main__':
    result = update(source_path, destination_path, index_path, backup_path, backup_2_path)
    print("Updated the configuration successfully." if result else "Failed to update.")
