import subprocess


def read_requirements(file_path):
    """讀取requirements.txt

    Args:
        file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(file_path, "r",encoding="utf-8") as file:
        return [line.strip() for line in file]

def get_installed_packages():
    """獲取安裝的套件

    Returns:
        _type_: _description_
    """
    installed_packages = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
    return [line.strip() for line in installed_packages.splitlines()]

def find_missing_packages(requirements, installed_packages):
    """找出還未新增在requirements.txt的套件

    Args:
        requirements (_type_): _description_
        installed_packages (_type_): _description_

    Returns:
        _type_: _description_
    """
    return [package for package in installed_packages if package not in requirements]

def update_requirements(requirements_path, missing_packages):
    """新增套件到requirements.txt中

    Args:
        requirements_path (_type_): _description_
        missing_packages (_type_): _description_
    """
    with open(requirements_path, "a",encoding="utf-8") as file:
        for package in missing_packages:
            file.write(package + "\n")

def main():
    requirements_path = "requirements.txt"
    installed_packages = get_installed_packages()
    requirements = read_requirements(requirements_path)
    missing_packages = find_missing_packages(requirements, installed_packages)

    if missing_packages:
        print("Missing packages found in the environment but not listed in requirements.txt:")
        for package in missing_packages:
            print(package)
        update_requirements(requirements_path, missing_packages)
        print("requirements.txt has been updated.")
    else:
        print("No missing packages found. requirements.txt is up to date.")

if __name__ == "__main__":
    main()
