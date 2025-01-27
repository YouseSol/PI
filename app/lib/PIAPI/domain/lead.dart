class Lead {
  String owner;

  int id;

  String linkedinPublicIdentifier;
  String? chatId;

  String firstName, lastName;

  List<String> emails;
  List<String> phones;

  bool active;

  Lead({
    required this.owner,
    required this.id,
    required this.linkedinPublicIdentifier,
    required this.chatId,
    required this.firstName,
    required this.lastName,
    required this.emails,
    required this.phones,
    required this.active,
  });

  Lead.fromMap(Map obj):
    owner = obj["owner"] as String,
    id = obj["id"] as int,
    linkedinPublicIdentifier = obj["linkedin_public_identifier"] as String,
    chatId = obj["chat_id"] as String?,
    firstName = obj["first_name"] as String,
    lastName = obj["last_name"] as String,
    emails = (obj["emails"] as List<dynamic>).cast<String>(),
    phones = (obj["phones"] as List<dynamic>).cast<String>(),
    active = obj["active"] as bool;

  Map toJson() {
    return {
      'owner': owner,
      'id': id,
      'linkedin_public_identifier': linkedinPublicIdentifier,
      'chat_id': chatId,
      'first_name': firstName,
      'last_name': lastName,
      'emails': emails,
      'phones': phones,
      'active': active
    };
  }
}
