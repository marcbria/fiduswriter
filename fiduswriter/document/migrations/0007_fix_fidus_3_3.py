import os
import json
import zipfile
import tempfile
from decimal import Decimal

from django.db import migrations
from django.core.files import File

# Some Fidus Writer 3.9.0 and 3.9.1 installations will have empty table cells
FW_DOCUMENT_VERSION = 3.3

ID_COUNTER = 0


def update_initial_node(node):
    global ID_COUNTER
    if "type" in node:
        if node["type"] in ["bullet_list", "ordered_list"]:
            if "attrs" not in node:
                node["attrs"] = {}
            ID_COUNTER += 1
            if "id" not in node["attrs"]:
                node["attrs"]["id"] = "{}{:0>8d}".format("L", ID_COUNTER)
        elif node["type"] == "table" and "content" in node:
            if "attrs" not in node:
                node["attrs"] = {}
            ID_COUNTER += 1
            if "id" not in node["attrs"]:
                node["attrs"]["id"] = "{}{:0>8d}".format("T", ID_COUNTER)
                node["attrs"]["caption"] = False
                if "content" in node:
                    node["content"] = [
                        {"type": "table_caption"},
                        {"type": "table_body", "content": node["content"]},
                    ]
        elif node["type"] == "table_cell" and (
            "content" not in node or len(node["content"]) == 0
        ):
            node["content"] = [{"type": "paragraph"}]
        elif node["type"] == "figure":
            if "attrs" not in node:
                node["attrs"] = {}
            attrs = node["attrs"]
            if "category" in attrs:
                # Already updated
                return
            if "figureCategory" in attrs:
                attrs["category"] = attrs["figureCategory"]
                del attrs["figureCategory"]
            else:
                attrs["category"] = "none"
            node["content"] = []
            if "image" in attrs and attrs["image"] is not False:
                node["content"].append(
                    {"type": "image", "attrs": {"image": attrs["image"]}}
                )
            else:
                equation = ""
                if "equation" in attrs:
                    equation = attrs["equation"]
                node["content"].append(
                    {
                        "type": "figure_equation",
                        "attrs": {"equation": equation},
                    }
                )
            if "image" in attrs:
                del attrs["image"]
            if "equation" in attrs:
                del attrs["equation"]
            caption = {"type": "figure_caption"}
            if (
                "caption" in attrs
                and attrs["caption"] is not False
                and len(attrs["caption"]) > 0
            ):
                caption["content"] = [
                    {"type": "text", "text": attrs["caption"]}
                ]
                attrs["caption"] = True
            else:
                attrs["caption"] = False
            if attrs["category"] == "table":
                node["content"].insert(0, caption)
            else:
                node["content"].append(caption)
            node["attrs"] = attrs
    if "content" in node:
        for sub_node in node["content"]:
            update_initial_node(sub_node)


def update_node(node):
    if "contents" in node:  # revision
        update_node(node["contents"])
    if "type" in node:
        if node["type"] == "table_cell" and (
            "content" not in node or len(node["content"]) == 0
        ):
            node["content"] = [{"type": "paragraph"}]
    if "content" in node:
        for sub_node in node["content"]:
            update_node(sub_node)
    if (
        "attrs" in node
        and "initial" in node["attrs"]
        and bool(node["attrs"]["initial"])
    ):
        for sub_node in node["attrs"]["initial"]:
            update_initial_node(sub_node)


# from https://stackoverflow.com/questions/25738523/how-to-update-one-file-inside-zip-file-using-python
def update_revision_zip(file_field, file_name):
    # generate a temp file
    tmpfd, tmpname = tempfile.mkstemp()
    os.close(tmpfd)
    # create a temp copy of the archive without filename
    with zipfile.ZipFile(file_field.open(), "r") as zin:
        with zipfile.ZipFile(tmpname, "w") as zout:
            zout.comment = zin.comment  # preserve the comment
            for item in zin.infolist():
                if item.filename == "document.json":
                    doc_string = zin.read(item.filename)
                    doc = json.loads(doc_string)
                    if "contents" in doc:
                        doc["content"] = doc["contents"]
                        del doc["contents"]
                    update_node(doc["content"])
                    zout.writestr(item, json.dumps(doc))
                else:
                    zout.writestr(item, zin.read(item.filename))
    # replace with the temp archive
    with open(tmpname, "rb") as tmp_file:
        file_field.save(file_name, File(tmp_file))
    os.remove(tmpname)


def update_documents(apps, schema_editor):
    Document = apps.get_model("document", "Document")
    documents = Document.objects.all().iterator()
    for document in documents:
        if document.doc_version == Decimal(str(FW_DOCUMENT_VERSION)):
            update_node(document.content)
            for field in document._meta.local_fields:
                if field.name == "updated":
                    field.auto_now = False
            document.save()

    DocumentTemplate = apps.get_model("document", "DocumentTemplate")
    templates = DocumentTemplate.objects.all()
    for template in templates:
        if template.doc_version == Decimal(str(FW_DOCUMENT_VERSION)):
            update_node(template.content)
            template.save()

    DocumentRevision = apps.get_model("document", "DocumentRevision")
    revisions = DocumentRevision.objects.all()
    for revision in revisions:
        if not revision.file_object:
            revision.delete()
            continue
        if revision.doc_version == Decimal(str(FW_DOCUMENT_VERSION)):
            update_revision_zip(revision.file_object, revision.file_name)


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0006_auto_20201209_1610"),
    ]

    operations = [
        migrations.RunPython(update_documents),
    ]
