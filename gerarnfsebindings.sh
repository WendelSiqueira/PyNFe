#!/bin/sh
# Regenera os bindings PyXB da NFS-e (Betha e Ginfes) a partir dos XSDs.
#
# Uso (na raiz do projeto ou de qualquer lugar):
#   uv sync --extra nfse
#   uv run ./gerarnfsebindings.sh
#
# O pyxbgen grava o caminho de cada XSD no codigo gerado. O script troca o
# caminho absoluto da maquina por um caminho relativo a raiz do projeto, para
# a saida ser a mesma em qualquer maquina, e formata com o ruff no final.

set -eu

raiz="$(cd "$(dirname "$0")" && pwd)"
cd "$raiz"

xsd_path="pynotas/data/XSDs/"
bindings_root_path="pynotas/utils/"

exige() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "erro: '$1' nao encontrado. Rode com: uv sync --extra nfse && uv run ./gerarnfsebindings.sh" >&2
        exit 1
    fi
}

main() {
    exige pyxbgen
    exige ruff

    main_xsd_nfse_path="${xsd_path}NFS-e/"
    main_bindings_root_nfse_path="${bindings_root_path}nfse/"

    gera_bindings_diretorio "${main_xsd_nfse_path}Betha/" "${main_bindings_root_nfse_path}betha/"
    ajustes_betha "${main_bindings_root_nfse_path}betha/"

    gera_bindings_diretorio "${main_xsd_nfse_path}Ginfes/" "${main_bindings_root_nfse_path}ginfes/"
    ajustes_ginfes "${main_bindings_root_nfse_path}ginfes/"

    caminhos_relativos "${main_bindings_root_nfse_path}"
    ruff format --quiet "${main_bindings_root_nfse_path}"
    echo "Bindings gerados em ${main_bindings_root_nfse_path}"
}

gera_binding() {
    pyxbgen \
        --schema-location="$1" \
        --module="$2" \
        --binding-root="$3"
}

gera_bindings_diretorio() {
    gbd_xsd_nfse_path="$1"
    gbd_bindings_root_nfse_path="$2"

    for file in "$gbd_xsd_nfse_path"*.xsd; do
        if [ -f "$file" ]; then
            filename="${file##*/}"     # apenas o nome do arquivo - Ex: schema.xsd
            basename="${filename%.*}"  # sem a extensao - Ex: schema

            echo "Gerando: $basename"
            gera_binding "$gbd_xsd_nfse_path${basename}.xsd" "$basename" "$gbd_bindings_root_nfse_path"
        fi
    done

    ignorar_lint "$gbd_bindings_root_nfse_path"
}

# Codigo gerado nao passa pelo lint (o ruff respeita "# flake8: noqa")
ignorar_lint() {
    for file in "$1"*.py; do
        filename="${file##*/}"
        if [ -f "$file" ] && [ "$filename" != "__init__.py" ]; then
            sed -i '1i# flake8: noqa' "$file"
        fi
    done
}

# Troca "<raiz absoluta>/pynotas/..." por "pynotas/..." nos arquivos gerados
caminhos_relativos() {
    raiz_escapada="$(printf '%s/' "$raiz" | sed 's/[][\.*^$|]/\\&/g')"
    for file in "$1"*/*.py; do
        if [ -f "$file" ]; then
            sed -i "s|${raiz_escapada}||g" "$file"
        fi
    done
}

ajustes_betha() {
    rm -f "${1}xmldsig_core_schema20020212.py"

    for file in "$1"*.py; do
        filename="${file##*/}"
        if [ -f "$file" ] && [ "$filename" != "__init__.py" ]; then
            sed -i 's/import _dsig/from pynotas.utils.nfse.betha import _dsig/g' "$file"
        fi
    done
}

ajustes_ginfes() {
    rm -f "${1}tipos_v03.py"
    rm -f "${1}xmldsig_core_schema20020212_v03.py"

    for file in "$1"*.py; do
        filename="${file##*/}"
        if [ -f "$file" ] && [ "$filename" != "__init__.py" ]; then
            sed -i 's/import _dsig/from pynotas.utils.nfse.ginfes import _dsig/g' "$file"
            sed -i 's/import _tipos/from pynotas.utils.nfse.ginfes import _tipos/g' "$file"
        fi
    done
}

main
