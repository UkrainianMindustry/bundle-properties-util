import os
import hjson


def get(stroke, start="", end=""):
    if start != "":
        stroke = stroke[stroke.find(start) + len(start):]
    if end != "" and (end in stroke):
        stroke = stroke[0:stroke.find(end)]
    return stroke


def list_paths(directory, is_file):
    for path in os.listdir(directory):
        if os.path.isdir(directory + "\\" + path) != is_file:
            yield directory + "\\" + path


class Methods:
    name = ""
    bundle = []

    def parse_f(self, file):
        mod = ""
        if "mod." in file:
            self.name = hjson.loads(open(file, "r").read())["name"]
        if not ("content" in file): return
        if not ((".json" in file) or (".hjson" in file)): return
        name = get(file, "\\")
        n_n = name.count("\\")
        while n_n > 0:
            n_n = name.count("\\")
            name = get(name, "\\")

        p_type = get(file, start="content\\", end="\\")
        p_name = get(name, end=".")

        file_dict = hjson.loads((open(file, "r").read() + "\n").replace("]\n", "\n]\n"))

        if "localizedName" in file_dict.keys():
            p_lname = "\"" + file_dict["localizedName"] + "\""
        else:
            p_lname = " ".join([n.capitalize() for n in p_name.split("-")])

        line_n = p_type + "." + self.name + "-" + p_name + ".name = " + p_lname
        # print(line_n)
        self.bundle.append(line_n)

        if "description" in file_dict.keys():
            line_d = p_type + "." + self.name + "-" + p_name + ".description = \"" + file_dict["description"] + "\""
            # print(line_d)
            self.bundle.append(line_d)

    def parse_d(self, dir):
        for f in list_paths(dir, True):  # files
            try:
                self.parse_f(f)
            except Exception:
                print(f)
                raise Exception

        for d in list_paths(dir, False):  # dirs
            self.parse_d(d)

    def parse_a(self, d):
        self.parse_d(d)


if __name__ == "__main__":
    m = Methods()
    d = input("put json mod directory: ")
    while not os.path.isdir(d):
        d = input("\nthis is invalid directory.\nput valid json mod directory: ")

    print()
    m.parse_a(d)
    if not os.path.exists(d+"\\bundles"):
        os.mkdir(d+"\\bundles")

    with open(d+"\\bundles\\bundle_new.properties", "w") as tf:
        tf.write("\n".join(m.bundle))

    print(f"Successful created {d}\\bundles\\bundle_new.properties")
