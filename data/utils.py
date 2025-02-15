from aiida import load_profile, orm
import os
import argparse
from aiida_pseudo.data.pseudo import UpfData

# Load AiiDA profile
load_profile()


def main():
    parser = argparse.ArgumentParser(
        description="Create a pseudo group and add pseudos."
    )
    parser.add_argument("folder_path", help="Path to the data folder (local or full).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the process without modifying AiiDA.",
    )

    args = parser.parse_args()

    # Normalize the path (support both local and absolute paths)
    folder_path = os.path.abspath(args.folder_path)

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    group_label = os.path.basename(folder_path)

    # Check if the group already exists
    builder = orm.QueryBuilder()
    builder.append(orm.Group, filters={"label": group_label})
    existing_group = builder.first()

    if existing_group is None:
        if args.dry_run:
            print(f"[Dry-Run] Would create new group: {group_label}")
            group = None  # Placeholder to avoid errors
        else:
            group = orm.Group(label=group_label).store()
            print(f"Created new group: {group_label}")
    else:
        group = existing_group[0]
        print(f"Using existing group: {group_label}")

    # Add .UPF files to the group
    for file in os.listdir(folder_path):
        if file.endswith(".UPF"):
            label = file.split(".")[0]
            labels = [node.label for node in group.nodes] if group else []

            if label in labels:
                print(f"Skipping {file}: Already in group.")
                continue

            if args.dry_run:
                print(f"[Dry-Run] Would add {file} to group {group_label}.")
            else:
                pseudo = UpfData(os.path.join(folder_path, file))
                pseudo.label = label
                pseudo.store()
                print(f"Added {label}: {pseudo.pk}")
                group.add_nodes(pseudo)

    # Archive the group
    archive_name = f"{group_label}.aiida"

    if args.dry_run:
        print(f"[Dry-Run] Would create archive: {archive_name}")
    else:
        if os.path.exists(archive_name):
            os.remove(archive_name)
        os.system(f"verdi archive create {archive_name} --groups {group_label}")
        print(f"Archive created: {archive_name}")


if __name__ == "__main__":
    main()
