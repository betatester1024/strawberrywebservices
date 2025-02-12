

if __name__ == "__main__":
    def log(*logged):
        s = ""
        for x in logged:
            s += str(x) + " "
        text = f'[2;30m{datetime.now().strftime("%H:%M:%S:%f")[:-3]} // [0m[2;36m[EventDiscord][0m ' + s + "[0m"
        print("[2;31m[TEST SUITE][0m " + text)
    loggerTest = Econlogger(log)
    # loggerTest.fetch()
    title, desc, raw = loggerTest.find_dst_by_hex("6468")
    print(raw)
    print(title)
    print(desc)
