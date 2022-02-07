import os
import hjson_parser


def list_paths(directory, is_file):
    for path in os.listdir(directory):
        if os.path.isdir(directory + "\\" + path) != is_file:
            yield directory + "\\" + path


class Methods:
    name = ""
    bundle = []
    category = ["", ""]

    def parse_f(self, file):
        mod = ""
        if "mod." in file:
            self.name = hjson_parser.parser.parse(open(file, "r").read())["name"]
        if not ("content" in file): return
        if not ((".json" in file) or (".hjson" in file)): return
        name = hjson_parser.get(file, "\\")
        n_n = name.count("\\")
        while n_n > 0:
            n_n = name.count("\\")
            name = hjson_parser.get(name, "\\")

        p_type = hjson_parser.get(file, start="content\\", end="\\")
        p_name = hjson_parser.get(name, end=".")

        file_dict = hjson_parser.parser.parse((open(file, "r").read() + "\n").replace("]\n", "\n]\n"), log_p)

        if "localizedName" in file_dict.keys():
            p_lname = file_dict["localizedName"]
        else:
            p_lname = " ".join([n.capitalize() for n in p_name.split("-")])

        line_n = p_type + "." + self.name + "-" + p_name + ".name = " + p_lname
        # print(line_n)
        self.bundle.append(line_n)

        if "description" in file_dict.keys():
            line_d = p_type + "." + self.name + "-" + p_name + ".description = " + file_dict["description"]
            # print(line_d)
            self.bundle.append(line_d.replace("\n", "\\n"))

    def parse_d(self, dir):
        if "content\\" in dir:
            new_category = ["", ""]
            folder = hjson_parser.get(dir, "content\\")
            new_category[0] = hjson_parser.get(folder, end="\\")
            new_category[1] = hjson_parser.get(folder, new_category[0]+"\\", "\\")

            NSOF = bool(len(self.bundle))  # Not Start Of File
            if new_category[0] != self.category[0]:
                self.bundle.append("\n\n"*NSOF+"# "+new_category[0].capitalize())

            NFC = ([""]+self.bundle)[-1].replace("\n", "")[:2] != "# "   # Not First Category
            if new_category[1] != self.category[1]:
                if new_category[1] == "":
                    new_category[1] = "other"
                self.bundle.append("\n"*NFC+"## "+new_category[1].capitalize())
            self.category = new_category

        for f in list_paths(dir, True):  # files
            try:
                self.parse_f(f)
            except Exception:
                raise Exception(f"in {f}")  # print file that occurred error

        for d in list_paths(dir, False):  # dirs
            self.parse_d(d)

    def parse_a(self, d):
        self.parse_d(d)


if __name__ == "__main__":
    log_p = False
    log_s = True

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
