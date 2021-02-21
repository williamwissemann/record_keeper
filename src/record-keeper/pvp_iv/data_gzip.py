import gzip
import shutil
import os

path = "/Users/wtw/Downloads/raw/"
outpath = "/Users/wtw/Dropbox/docker/record-keeper/discord_bot/pvp_iv/compressed/"
dirs = os.listdir(path)
for dir in dirs:
    if "." not in dir:
        try:
            os.mkdir(outpath)
        except:
            pass
        try:
            os.mkdir(outpath + dir)
        except:
            pass

        items = os.listdir(path + "/" + dir)
        for names in items:
            if names.endswith(".csv"):
                print()
                infile = path + dir + "/" + names
                clean_name = names.replace(" ", "")
                clean_name = clean_name.replace("(", "")
                clean_name = clean_name.replace(")", "")
                clean_name = clean_name.replace("Cloak", "")
                clean_name = clean_name.replace("Forme", "")
                clean_name = clean_name.replace("Ho-Oh", "HoOh")
                outfile = outpath + dir + "/" + clean_name + ".gz"
                print(infile)
                print(outfile)
                with open(infile, 'rb') as f_in, gzip.open(outfile, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
