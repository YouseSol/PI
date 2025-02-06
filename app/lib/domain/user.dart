class User {
  String firstName, lastName;
  String email;
  String token;
  bool active;

  User({
    required this.firstName, required this.lastName,
    required this.email,
    required this.token,
    required this.active
  });

  User.fromMap(Map obj):
    firstName = obj["first_name"] as String,
    lastName = obj["last_name"] as String,
    email = obj["email"] as String,
    token = obj["token"] as String,
    active = obj["active"] as bool;
}
