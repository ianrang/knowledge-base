# NIST SP 800-63B — Multi-Factor Cryptographic Devices and AAL2

- Source: https://pages.nist.gov/800-63-3/sp800-63b.html
- Retrieved: 2026-09-13
- Extracted for: whether unlocking a device-bound credential with a PIN counts as a
  second authentication factor, versus unlocking it with a biometric.

## Section 5.1.9 — Multi-Factor Cryptographic Devices

> A multi-factor cryptographic device is a hardware device that performs cryptographic
> operations using one or more protected cryptographic keys and requires activation
> through a second authentication factor.

The two factors are (a) possession of the hardware device and (b) activation through
either a memorized secret or a biometric.

## Section 5.1.9.1 — Multi-Factor Cryptographic Device Authenticators

> the authenticator operates by using a private key that was unlocked by the additional
> factor, either a memorized secret or a biometric

Both activation methods satisfy the second-factor requirement.

## Section 4.2 — Authenticator Assurance Level 2

> Proof of possession and control of two distinct authentication factors is required
> through secure authentication protocol(s).

At AAL2 a single multi-factor device satisfies both factors on its own; no separate
password is required.
