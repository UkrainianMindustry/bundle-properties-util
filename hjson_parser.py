def get(stroke, start="", end=""):
    if start != "":
        stroke = stroke[stroke.find(start) + len(start):]
    if end != "" and (end in stroke):
        stroke = stroke[0:stroke.find(end)]
    return stroke


def remove(stroke, start="", end=""):
    start_i = stroke.find(start)
    end_i = start_i + stroke[start_i:].find(end)
    if end == "": end_i = len(stroke) - 1
    return stroke[:start_i] + stroke[end_i:]


q3 = "'''"
q2 = '"'
q1 = "'"
d = "{"
l = "["
t = "("
test = -1  # 500 + 250 + 3
log = False


def remove_fs(string, ch):
    while string[:1] in ch:
        string = string[1:]
    return string


def remove_fe(string, ch):
    while string[-1:] in ch:
        string = string[:-1]
    return string


def remove_fc(string, ch):
    return remove_fs(remove_fe(string, ch), ch)


def brackets(file_t):
    tags = {"{": "}", "[": "]", "(": ")", "\"": "\"", "'": "'", "//": "\n"}
    cut = ["", 0]
    var_n = []
    new_file_t = ""
    if log: print("log/brackets [file_t]: ", file_t)

    for i in range(len(file_t)):
        l = file_t[i]
        #  if log: print("log/brackets/for [cut, l]: ", cut, l)
        if not cut[1]:
            if file_t[i:i + 2] == "//":
                var_n += [l]
                cut[0] = "//"
                cut[1] += 1
            elif l in tags.keys():
                check_l = l
                ti = i
                hist = ""
                while ti > 0:
                    if check_l not in (" ", "\t"):
                        hist += check_l
                    ti -= 1
                    check_l = file_t[ti]
                    if check_l in (":", "[", "(", "{"):
                        break
                if ti == 0:
                    hist = "{" + hist
                if check_l not in ("(", "["):
                    if not hist[1:-1]:
                        var_n += [l]
                        cut[0] = l
                        cut[1] += 1
                else:
                    hist = hist.replace("\n", ",")
                    if not hist[1:-1]:
                        var_n += [l]
                        cut[0] = l
                        cut[1] += 1
                    elif "," in hist:
                        if not get(hist, "\"", ","):
                            var_n += [l]
                            cut[0] = l
                            cut[1] += 1
                if not cut[1]:
                    new_file_t += l
            else:
                new_file_t += l
        else:
            var_n[-1] += l
            if l == tags[cut[0]]:
                cut[1] -= 1
                if cut[1] == 0:
                    if cut[0] != "//":
                        new_file_t += f"var_n{len(var_n)}_"
                    cut[0] = ""
            elif l == cut[0]:
                cut[1] += 1
    var_n = [var for var in var_n if var[:2] != "//"]
    if log: print("log/brackets/end [new_file_t, var_n]: ", new_file_t, var_n, "\n--")
    return new_file_t, var_n


class list_parser:
    @staticmethod
    def parse_l(file_t):
        if file_t[:1] in "[(" and file_t[-1:] in "])":
            file_t = file_t[1:-1]
        else:
            raise Exception(f"|{file_t}| isn't list")

        new_file_t, var_n = brackets(file_t)

        file_l = new_file_t.replace(", ", ",").replace("\n", ",").split(",")
        var_n = [parser.parse_c(var) for var in var_n]

        new_file_l = []
        for el in file_l:
            if "var_n" in el:
                el = var_n[int(get(el, "var_n", "_")) - 1]
            new_file_l.append(el)
        return new_file_l

    def __init__(self):
        file_t = """[a, [b, c]]"""
        print("output/init/list_parser: ", list_parser.parse_l(file_t))


class string_parser:
    def parse_s(file_t):
        if file_t[:3] == q3 and file_t[-3:] == q3:
            new_file_s = file_t[3:-3]
        elif file_t[:1] == q2 and file_t[-1:] == q2:
            new_file_s = file_t[1:-1]
        elif file_t[:1] == q1 and file_t[-1:] == q1:
            new_file_s = file_t[1:-1]
        else:
            raise Exception(f"|{file_t}| isn't quoted string")
        if len(new_file_s) > 0:
            while new_file_s[0] == " ":
                new_file_s = new_file_s[1:]
        return new_file_s

    def __init__(self):
        file_t = "'''text'''"
        print("output/init/string_parser: ", string_parser.parse_s(file_t))


class parser:

    @staticmethod
    def parse_c(file_t):
        if log: print("log/parser/parse_c [file_t]: ", file_t, end="\n--------\n")
        if file_t[0] == q2 or file_t[0] == q1:
            return string_parser.parse_s(file_t)
        elif file_t[0] == d:
            return dict_parser.parse_d(file_t[1:-1])
        elif file_t[0] == l or file_t[0] == t:
            return list_parser.parse_l(file_t)
        else:
            return file_t

    @staticmethod
    def parse(file_t, log_=False):
        global log
        log = log_

        file_t = remove_fc(file_t, ("\n", " ",)).replace("\t", " ")

        if file_t[:1] == "{":
            if file_t[-1:] != "}":
                raise Exception("invalid json, not found closing braket \"}\"")
        else:
            file_t = "{" + file_t + "}"

        file_t = file_t.replace("'''", "'")
        return parser.parse_c(file_t)

    def __init__(self):
        file_t = """{c: "hello", b: [a, b]}"""
        print("output/init/parser: ", parser.parse_c(file_t))


class dict_parser:
    @staticmethod
    def parse_d(file_t):

        new_file_t, var_n = brackets(file_t)

        new_file_t = new_file_t.replace(": ", ":").replace(", ", ",")

        t = new_file_t.split("\n")
        t = [remove_fc(i, (" ", "\n")) for i in t]
        t = [x for x in t if x]
        t_t = []
        i = 0
        while i + 1 < len(t):
            if t[i][-1] == ":":
                t_t.append(t[i] + t[i + 1])
                i += 2
            else:
                t_t.append(t[i])
                i += 1
        t = t_t
        k = []
        v = []
        if log: print("log/dict_parser/parse_d [t]: ", t)
        for i in t:
            if log: print("log/dict_parser/parse_d/for [i]: ", i, end="|\n")
            if ":" not in i: raise Exception(": not in " + i)
            k += [i.split(":")[0]]
            v += [i.split(":")[1]]
            if log: print("log/dict_parser/parse_d/for [k, v]: ", k, v)

        if log: print("log/dict_parser/parse_d [k, v]: ", k, "\n", v, end="\n----\n")

        file_d = dict(zip(k, v))

        var_n = [parser.parse_c(var) for var in var_n]

        new_file_d = {}
        for k in file_d.keys():
            v = file_d[k]
            if "var_n" in k:
                k = var_n[int(get(k, "var_n", "_")) - 1]
            if "var_n" in v:
                v = var_n[int(get(v, "var_n", "_")) - 1]

            if type(k) == str:
                if len(k) > 1:
                    while k[0] == " ": k = k[1:]
            if type(v) == str:
                if len(v) > 1:
                    while v[0] == " ": v = v[1:]
            new_file_d[k] = v
        return new_file_d

    def __init__(self):
        file_t = """
a: {b:"c"}, b: rt
"""
        print("output/dict_parser/init: ", dict_parser.parse_d(file_t))


if __name__ == "__main__":
    # file_t = """a: [a, {a:"w\nn"}]"""
    # res = parser.parse(file_t)
    res = remove("test1 //test2\n test3\n//test4", "//", "\n")
    print("output/main: \n", res)
