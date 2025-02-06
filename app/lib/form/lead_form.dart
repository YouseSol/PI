import 'dart:developer';

import 'package:flutter/material.dart';

import 'package:pi/API/client.dart';
import 'package:pi/API/lead_api_extension.dart';

import 'package:pi/domain/lead.dart';


class LeadForm extends StatefulWidget {
  final PIClient apiClient;
  final Lead lead;
  final bool shouldPop;

  const LeadForm({ super.key, required this.apiClient, required this.lead, this.shouldPop = false });

  @override
  State<LeadForm> createState() => _LeadForm();
}

class _LeadForm extends State<LeadForm> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController firstNameController = TextEditingController();
  final TextEditingController lastNameController = TextEditingController();
  bool isActive = true;

  bool isLoading = false;

  @override
  void initState() {
    super.initState();

    firstNameController.text = widget.lead.firstName;
    lastNameController.text = widget.lead.lastName;
    isActive = widget.lead.active;
  }

  @override
  Widget build(BuildContext context) {
    final firstNameFormField = TextFormField(
      controller: firstNameController,
      decoration: const InputDecoration(border: OutlineInputBorder(),
                                        label: Text("Primeiro Nome"),
                                        floatingLabelBehavior: FloatingLabelBehavior.auto)
    );

    final lastNameFormField = TextFormField(
      controller: lastNameController,
      decoration: const InputDecoration(border: OutlineInputBorder(),
                                        label: Text("Ultimo Nome"),
                                        floatingLabelBehavior: FloatingLabelBehavior.auto)
    );

    final isActiveSwitch = Switch(
      value: isActive,
      onChanged: (value) => setState(() => isActive = value)
    );

    final saveButton = TextButton(onPressed: saveLead, child: const Text("Salvar"));

    const divider = Divider(color: Colors.transparent);

    final column = <Widget>[
      if (!isLoading) ...[
        firstNameFormField,
        divider,
        lastNameFormField,
        divider,
        Row(children: [ const Expanded(child: Text("Ativo", textScaler: TextScaler.linear(1.25))), isActiveSwitch ]),
        saveButton
      ],
      if (isLoading) ... const [
        Center(child: Text("Salvando")),
        divider,
        Center(heightFactor: 0.5, child: CircularProgressIndicator())
      ]
    ];

    return SingleChildScrollView(child: Form(
      autovalidateMode: AutovalidateMode.always,
      key: _formKey,
      child: Container(
        padding: const EdgeInsets.all(8.0),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: column)
      )
    ));
  }

  void saveLead() async {
    setState(() => isLoading = true);

    await widget.apiClient.saveLead(Lead(
      campaign: widget.lead.campaign,
      active: isActive,
      firstName: firstNameController.text,
      lastName: lastNameController.text,
      emails: widget.lead.emails,
      phones: widget.lead.phones,
      linkedinPublicIdentifier: widget.lead.linkedinPublicIdentifier,
      id: widget.lead.id,
      chatId: widget.lead.chatId,
    ));

    if (widget.shouldPop) {
      if (mounted) {
        Navigator.of(context).pop();
      }
    }
  }
}
