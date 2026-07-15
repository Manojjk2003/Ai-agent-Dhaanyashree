from app.services.firebase_service import FirebaseService


def main() -> None:
    service = FirebaseService()
    db = service._ensure_db()

    migrated = {"products": 0, "generated_posts": 0}
    for business_doc in db.collection("businesses").stream():
        business_id = business_doc.id
        for collection_name in ["products", "generated_posts"]:
            for doc in business_doc.reference.collection(collection_name).stream():
                data = doc.to_dict() or {}
                data["business_id"] = business_id
                db.collection(collection_name).document(doc.id).set(data, merge=True)
                migrated[collection_name] += 1

    print(migrated)
    print("top products", [doc.id for doc in db.collection("products").stream()])
    print(
        "top generated_posts",
        [doc.id for doc in db.collection("generated_posts").stream()],
    )


if __name__ == "__main__":
    main()
