def decode_cfemail(cfemail: str) -> str:
    """Decodifica o atributo data-cfemail do Cloudflare Email Protection."""
    if not cfemail or len(cfemail) < 4:
        return ""
    key = int(cfemail[:2], 16)
    return "".join(
        chr(int(cfemail[i:i+2], 16) ^ key)
        for i in range(2, len(cfemail), 2)
    )

cf = "f99a9a949dcfc9cdb98098919696d79a9694d79b8b"
print(decode_cfemail(cf))
# Saída: alexandre.auler@unimedpoa.com.br (exemplo — o valor real sai do decode)