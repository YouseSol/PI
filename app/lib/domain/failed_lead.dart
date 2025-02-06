class FailedLead {
  int id;
  int campaign;

  String firstName, lastName;
  String profileUrl;

  FailedLead({
    required this.id,
    required this.campaign,
    required this.firstName,
    required this.lastName,
    required this.profileUrl,
  });

  FailedLead.fromMap(Map obj):
    id = obj["id"] as int,
    campaign = obj["campaign"] as int,
    firstName = obj["first_name"] as String,
    lastName = obj["last_name"] as String,
    profileUrl = obj["profileUrl"] as String;

  Map toJson() {
    return {
      'id': id,
      'campaign': campaign,
      'first_name': firstName,
      'last_name': lastName,
      'profile_url': profileUrl,
    };
  }
}
