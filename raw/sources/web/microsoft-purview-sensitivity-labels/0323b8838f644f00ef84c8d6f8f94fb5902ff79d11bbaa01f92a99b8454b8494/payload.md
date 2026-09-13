# Microsoft Purview — Sensitivity labels: who may change a label

- Source: https://learn.microsoft.com/en-us/purview/sensitivity-labels
- Retrieved: 2026-09-13
- Extracted for: whether a user can change or remove an applied classification label,
  and what a downgrade requires.

## Default label may be changed by the user

> Users can change the applied default sensitivity label to better match the sensitivity
> of their content or container.

## Require a justification for changing a label

> **Require a justification for changing a label.** For files, emails, and meetings, but
> not for groups and sites (used by Teams and SharePoint), if a user tries to remove a
> label or replace it with a label that has a lower priority, by default the user must
> provide a justification to perform this action. For example, a user opens a document
> labeled Confidential (order number 3) and replaces that label with one named Public
> (order number 1). For Office apps, this justification prompt is triggered once per app
> session. When you use the Microsoft Purview Information Protection client, the prompt is
> triggered for each file. Administrators can read the justification reason along with the
> label change in activity explorer.

## Relationship to the older client

> The older labeling client, the Azure Information Protection unified labeling client, is
> now replaced with the Microsoft Purview Information Protection client.
