class Campaign {
  int id;

  String name;

  DateTime createdAt;

  bool active;

  Campaign({
    required this.id,
    required this.name,
    required this.createdAt,
    required this.active,
  });

  Campaign.fromMap(Map obj):
    id = obj["id"] as int,
    name = obj["name"] as String,
    createdAt = DateTime.parse(obj["created_at"] as String),
    active = obj["active"] as bool;

  Map toJson() {
    return {
      'id': id,
      'name': name,
      'created_at': createdAt,
      'active': active
    };
  }
}
