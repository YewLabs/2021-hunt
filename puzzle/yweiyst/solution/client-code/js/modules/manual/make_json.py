# TODO: run this to make sure yaml data is synced to json data
import base64, json, os, yaml

if __name__ == "__main__":
    b64s = {}

    for f in [f for f in os.listdir() if f[-4:] == ".png"]:
        with open(f, "rb") as f:
            b64s[
                f.name[:-4]
            ] = f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

    data = yaml.load(open("data.yaml"), Loader=yaml.SafeLoader)
    for k, v in b64s.items():
        data["images"][k] = v

    with open("data.yaml", "w") as f:
        f.write(yaml.dump(data, sort_keys=False))

    with open("data.js", "w") as f:
        f.write("const manualData = " + json.dumps(data) + "; export { manualData };")
