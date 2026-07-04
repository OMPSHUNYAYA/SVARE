from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path
from typing import Iterable, Optional, Union

VERSION = "10.0.6"
ENGINE_NAME = "SVARE Exact and Scientific Resolution"
DEFAULT_PRECISION = 30
MIN_PRECISION = 6
MAX_PRECISION = 120

CANONICALIZATION_VERSION = "2"
SEMANTIC_RULES_VERSION = "2"
CERTIFICATE_SCHEMA_VERSION = "2"
RESOURCE_POLICY_VERSION = "2"

MAX_INPUT_CHARACTERS = 10000
MAX_TOKEN_COUNT = 512
MAX_NESTING_DEPTH = 128
MAX_AST_NODES = 512
MAX_OPERATION_BUDGET = 4096
MAX_LITERAL_DIGITS = 4000
MAX_LITERAL_EXPONENT_ABS = 50000
MAX_EXACT_RESULT_DIGITS = 50000

if hasattr(sys, "set_int_max_str_digits"):
    try:
        sys.set_int_max_str_digits(MAX_EXACT_RESULT_DIGITS + 1000)
    except ValueError:
        pass

CONFORMANCE_VECTOR_SCHEMA_VERSION = "2"
CONFORMANCE_VECTOR_SHA256 = "76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69"
CONFORMANCE_VECTORS = [{'id': 'exact_decimal_residual',
  'expression': '1.0000000000000001 - 1',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1/10000000000000000',
               'decimal_approximation': '0.0000000000000001',
               'display_value': '0.0000000000000001',
               'display_mathematical_form': '1/10000000000000000',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'SUB(RAT(10000000000000001/10000000000000000),RAT(1/1))',
               'semantic_canonical': 'RAT(1/10000000000000000)',
               'structure_certificate_sha256': 'cb99f47d9c94bfe859cfea4c1ec5c6b721c8f0c92d2c3dbae46c9b5f29f66878',
               'semantic_certificate_sha256': '226d801fab1ba990899e2004f827b14eca7952d0915a15d85362e00380c58321',
               'display_receipt_sha256': 'c119552c418f0d5be2f4df351f20286b52fdc78e3decff94501cf131e16bed58',
               'error_code': None}},
 {'id': 'exact_integer_sqrt',
  'expression': 'sqrt(81)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '9',
               'decimal_approximation': '9',
               'display_value': '9',
               'display_mathematical_form': '9',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_SQRT(RAT(81/1))',
               'semantic_canonical': 'RAT(9/1)',
               'structure_certificate_sha256': 'd3bf92c5306e815041da878f03e82ba833ad71a0f3b9dc5adc1afff12c1e2e74',
               'semantic_certificate_sha256': 'a8e18d18dd1d8246d6e4972bed6edb3e6ac105b5ef84d8113d3b05a5594d10a6',
               'display_receipt_sha256': 'e1f95ec0606063b3f9bec44b172b9be93f7e89fbbc281153231f70e242746913',
               'error_code': None}},
 {'id': 'symbolic_sqrt',
  'expression': 'sqrt(2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': 'sqrt(2)',
               'decimal_approximation': '1.41421356237309504880168872421',
               'display_value': '≈ 1.41421356237309504880168872421',
               'display_mathematical_form': 'sqrt(2)',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_SQRT(RAT(2/1))',
               'semantic_canonical': 'SQRT(RAT(2/1))',
               'structure_certificate_sha256': '782cb9854390963f9c14640396d4cd44c1a376d23b010467a025508636d86d1f',
               'semantic_certificate_sha256': 'ae0edd959b1504c3c2cbe40f106ae167688c55d7cc64f1f3a290b2fe37a8004f',
               'display_receipt_sha256': '95afc70308d2d53cdd88d6cfa40160d2c0f7469b7e64ec2710723d00e499125a',
               'error_code': None}},
 {'id': 'sqrt_squared_identity',
  'expression': 'sqrt(2)^2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '2',
               'decimal_approximation': '2',
               'display_value': '2',
               'display_mathematical_form': '2',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(CALL_SQRT(RAT(2/1)),RAT(2/1))',
               'semantic_canonical': 'RAT(2/1)',
               'structure_certificate_sha256': '59a5ad03f4d198752402826997e601ff5aafaeeb1d5de6b0a1124d1e5e50da55',
               'semantic_certificate_sha256': 'bd09ae09776bfd0376ac1de59e0ba8209249d307a0346a7cbae59ecd7edd5e17',
               'display_receipt_sha256': '47e1693b908fbe62f52fcb4b202ec4452e51321c4a771f47c61f4a459e04fc4b',
               'error_code': None}},
 {'id': 'common_angle_sine',
  'expression': 'sin(pi/6)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1/2',
               'decimal_approximation': '0.5',
               'display_value': '0.5',
               'display_mathematical_form': '1/2',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_SIN(DIV(PI,RAT(6/1)))',
               'semantic_canonical': 'RAT(1/2)',
               'structure_certificate_sha256': '5d71e579d8b48a75741773255d23845318b45e0776cd827d1ee8075db7ea1af1',
               'semantic_certificate_sha256': 'ebb862b282b5ce44909f76f40e1146f26a9dddec4af97303276015454c580ada',
               'display_receipt_sha256': 'fd75ee05ad4eb3bfd399f1c246b5170c1abe86bf4de8e43da88ad816f365ffab',
               'error_code': None}},
 {'id': 'common_angle_cosine',
  'expression': 'cos(pi)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '-1',
               'decimal_approximation': '-1',
               'display_value': '-1',
               'display_mathematical_form': '-1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_COS(PI)',
               'semantic_canonical': 'RAT(-1/1)',
               'structure_certificate_sha256': 'cbd7d58f93e74e17d12f950b56f1ef0f46354a11eaa924bc56d838107c02c435',
               'semantic_certificate_sha256': 'ecd638e867610f01fe6b5e9fab0fd8b3a5afbd24936a7bf0ab1c08175939e2bc',
               'display_receipt_sha256': 'ec2c7fc8400ec7295dfb8a3373b28e8b5c443a338f4779d88e7c3841b28f8993',
               'error_code': None}},
 {'id': 'common_angle_tangent',
  'expression': 'tan(pi/4)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1',
               'decimal_approximation': '1',
               'display_value': '1',
               'display_mathematical_form': '1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_TAN(DIV(PI,RAT(4/1)))',
               'semantic_canonical': 'RAT(1/1)',
               'structure_certificate_sha256': 'f1f89df383361c9ad259b20bb8efe8e93ca32e6f09426075dffccb8cc2814992',
               'semantic_certificate_sha256': '7198cb7eb85ee7cee6bb638c0c547e07d3584a899a66429d5519bd90b7295d9e',
               'display_receipt_sha256': 'e8c568efa244891d52a1b165fa80cba7caa2cc401fec7be14a5d746e871540d2',
               'error_code': None}},
 {'id': 'tangent_singularity',
  'expression': 'tan(pi/2)',
  'precision': 30,
  'expected': {'state': 'SINGULAR',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': 'tan(pi/2)',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'CALL_TAN(DIV(PI,RAT(2/1)))',
               'semantic_canonical': 'SINGULAR',
               'structure_certificate_sha256': 'd5a1152e21f00280ea24a4aa968fec21a82954c248568e427879a5e5ca946e00',
               'semantic_certificate_sha256': '30570f99898d09cffb504b4f2ae48bbb68b37cd703a7b222c3551af9db8d0a36',
               'display_receipt_sha256': '23f424fa75a16f508640b9c889ed33f1a238aea32e2ed6e65f638ba0b0be06d0',
               'error_code': None}},
 {'id': 'nested_domain_refusal',
  'expression': 'sqrt(ln(1/2))',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': 'sqrt(ln(1/2))',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'CALL_SQRT(CALL_LN(DIV(RAT(1/1),RAT(2/1))))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': '8ecbc1081dd26482cca2dc5c625a0555ccd8569ed440f9117b178d609d072eb7',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': '15675748763c5f96c50786b1d68a1331c98e922fa30ce29747f8e1bb14c890a6',
               'error_code': None}},
 {'id': 'base10_log_identity',
  'expression': 'log10(1000)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '3',
               'decimal_approximation': '3',
               'display_value': '3',
               'display_mathematical_form': '3',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_LOG10(RAT(1000/1))',
               'semantic_canonical': 'RAT(3/1)',
               'structure_certificate_sha256': '3edd3bda55673b01436878cd0ea3ad41a546aaa24d2d61491ade4031bcd218bf',
               'semantic_certificate_sha256': 'a558959295a11cc93b6356f0617867b5f4ad9ff155f31f37d4a67f75dbae914f',
               'display_receipt_sha256': '6bdffa3f1cd0629102a73f3982f4c93043707a7178f0720d81fc47e68ed41570',
               'error_code': None}},
 {'id': 'natural_log_identity',
  'expression': 'ln(e)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1',
               'decimal_approximation': '1',
               'display_value': '1',
               'display_mathematical_form': '1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_LN(E)',
               'semantic_canonical': 'RAT(1/1)',
               'structure_certificate_sha256': '25d953237e079b49b5321be0ce9152e95dd2fbc5ac87570c917e914903915abf',
               'semantic_certificate_sha256': '7198cb7eb85ee7cee6bb638c0c547e07d3584a899a66429d5519bd90b7295d9e',
               'display_receipt_sha256': 'e8c568efa244891d52a1b165fa80cba7caa2cc401fec7be14a5d746e871540d2',
               'error_code': None}},
 {'id': 'exponential_identity',
  'expression': 'exp(0)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1',
               'decimal_approximation': '1',
               'display_value': '1',
               'display_mathematical_form': '1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_EXP(RAT(0/1))',
               'semantic_canonical': 'RAT(1/1)',
               'structure_certificate_sha256': 'ee0ea6e95a998cb7c0239d3e6d1258d8c6c438c40bea709b198222ee1687afc0',
               'semantic_certificate_sha256': '7198cb7eb85ee7cee6bb638c0c547e07d3584a899a66429d5519bd90b7295d9e',
               'display_receipt_sha256': 'e8c568efa244891d52a1b165fa80cba7caa2cc401fec7be14a5d746e871540d2',
               'error_code': None}},
 {'id': 'inverse_sine_identity',
  'expression': 'asin(1/2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': '1/6 * pi',
               'decimal_approximation': '0.523598775598298873077107230547',
               'display_value': '≈ 0.523598775598298873077107230547',
               'display_mathematical_form': '1/6 * pi',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ASIN(DIV(RAT(1/1),RAT(2/1)))',
               'semantic_canonical': 'MUL(RAT(1/6),PI)',
               'structure_certificate_sha256': '8cd7110cac37ea72ad9a79127e7718d3a99b76561fb3ba60d92b10ff7b24b6b1',
               'semantic_certificate_sha256': '7f0257dab8aac4dcffbdd09d3082f01694e497407a8fd79509ad9902addaea99',
               'display_receipt_sha256': '4a6e35fca8f62e8a7c784f6df25bd32b645a0d2ede0f13c01bc81332afcd546d',
               'error_code': None}},
 {'id': 'inverse_cosine_identity',
  'expression': 'acos(0)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': '1/2 * pi',
               'decimal_approximation': '1.57079632679489661923132169164',
               'display_value': '≈ 1.57079632679489661923132169164',
               'display_mathematical_form': '1/2 * pi',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ACOS(RAT(0/1))',
               'semantic_canonical': 'MUL(RAT(1/2),PI)',
               'structure_certificate_sha256': '9b09ee9c601ad3c801604a47b76e1ea159abc21d89920b359a0b1213f1cb01a0',
               'semantic_certificate_sha256': '10e1034407d8036972bcd8028b8adc8246a982e093369e7a4f33d1e59c55b1a2',
               'display_receipt_sha256': '1e2a45c7a1aa1e13404fcb514495aebaad7da6939f9ea0a345294f657bcfcdc0',
               'error_code': None}},
 {'id': 'inverse_tangent_identity',
  'expression': 'atan(1)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': '1/4 * pi',
               'decimal_approximation': '0.78539816339744830961566084582',
               'display_value': '≈ 0.78539816339744830961566084582',
               'display_mathematical_form': '1/4 * pi',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ATAN(RAT(1/1))',
               'semantic_canonical': 'MUL(RAT(1/4),PI)',
               'structure_certificate_sha256': '919b45bb604439c3f3a9e15bb2ca9f1df1389c85972aa71671237d80be6c36ad',
               'semantic_certificate_sha256': 'd612efc6fde0a86ca62a751dc78b51b4a7a77c285a08c6c47c87e27dab256def',
               'display_receipt_sha256': '4bcac8069808dfae56143f5363ed4e0558e4e061d13197a8335b70ef62f03caa',
               'error_code': None}},
 {'id': 'degree_conversion',
  'expression': 'sin(deg(90))',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1',
               'decimal_approximation': '1',
               'display_value': '1',
               'display_mathematical_form': '1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_SIN(CALL_DEG(RAT(90/1)))',
               'semantic_canonical': 'RAT(1/1)',
               'structure_certificate_sha256': '0b0fc9529d82e33a1724b09c2c7f8921c7336aed52cd5dd29f3c43a80a2d7f94',
               'semantic_certificate_sha256': '7198cb7eb85ee7cee6bb638c0c547e07d3584a899a66429d5519bd90b7295d9e',
               'display_receipt_sha256': 'e8c568efa244891d52a1b165fa80cba7caa2cc401fec7be14a5d746e871540d2',
               'error_code': None}},
 {'id': 'negative_sqrt_refusal',
  'expression': 'sqrt(-1)',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': 'sqrt(-1)',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'CALL_SQRT(UNARY_MINUS(RAT(1/1)))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': 'fe30828256996c54b3d8f3865ab223c145b794efc101c68bee8d3cf6008b9f7e',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': '0f2d5da053534bd6e9756bf4edc821282ee60f96fc089a52ef46a2adcf584ef7',
               'error_code': None}},
 {'id': 'zero_log_refusal',
  'expression': 'ln(0)',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': 'ln(0)',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'CALL_LN(RAT(0/1))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': 'e0d72bc2de5384f3930c63c097cdeb43d11c355f72567bb17fe29fb8312e51ac',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': '4f9ea0d47aa6800ca5fc1defefa722cd15bdd5d104c64cb4615dee0dab2cd0a9',
               'error_code': None}},
 {'id': 'inverse_trig_domain_refusal',
  'expression': 'asin(2)',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': 'asin(2)',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'CALL_ASIN(RAT(2/1))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': '5b3e8623b950dd7c6313d31bb89d56a85bbf4f2c40d2d239be0645ec4286f953',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': 'f55b987b1f97fcd7c4f223c2b99a49e94d7fba6784c1d6ad363d40c2d7d8ba16',
               'error_code': None}},
 {'id': 'division_by_zero',
  'expression': '1/0',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': '1/0',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'DIV(RAT(1/1),RAT(0/1))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': '1c61be47a3290214c9521304440947d7cbf9172ad5fd1733bd49d1c2de4e8c31',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': '6785f8b339a023e090edd56396d134ba31f01c7bd574b34b623e70b1b990b8c1',
               'error_code': None}},
 {'id': 'indeterminate_zero_division',
  'expression': '0/0',
  'precision': 30,
  'expected': {'state': 'INDETERMINATE',
               'resolution_class': 'REFUSED',
               'display_kind': 'INDETERMINATE',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'indeterminate',
               'display_mathematical_form': '0/0',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'DIV(RAT(0/1),RAT(0/1))',
               'semantic_canonical': 'INDETERMINATE',
               'structure_certificate_sha256': 'b0e106799b96ac90f9e604f777527275ac0f062cc5a2bc8de43742ada7370199',
               'semantic_certificate_sha256': '6a8068d8b5bb74c6f628ed69b9f97c76eec5668a2422cd598d4fa84edb4e9f9a',
               'display_receipt_sha256': '4e6765e5afa1c56de7c94cd280944a8682398d34ae29b3ebc97767dba1efbce7',
               'error_code': None}},
 {'id': 'incomplete_group',
  'expression': '(1+2',
  'precision': 30,
  'expected': {'state': 'INCOMPLETE',
               'resolution_class': 'REFUSED',
               'display_kind': 'INCOMPLETE',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'incomplete',
               'display_mathematical_form': '(1+2',
               'display_form_label': 'Submitted expression',
               'structure_canonical': 'UNRESOLVED',
               'semantic_canonical': 'INCOMPLETE',
               'structure_certificate_sha256': '0846961325c1c5586c35cc30d24a305fe5404be3ec3977ab9943d71bcfed272e',
               'semantic_certificate_sha256': 'e77e3d61dc7204b1e8a05a7f7a3f7520644f1e6be5ed24f400aa2490d22c59a2',
               'display_receipt_sha256': 'c7ac94e2ed73f5756451ffadff17cbd4f0c677be42b74e412ae67f14f23cb632',
               'error_code': None}},
 {'id': 'integer_gcd',
  'expression': 'gcd(84,30,18)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '6',
               'decimal_approximation': '6',
               'display_value': '6',
               'display_mathematical_form': '6',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_GCD(RAT(18/1),RAT(30/1),RAT(84/1))',
               'semantic_canonical': 'RAT(6/1)',
               'structure_certificate_sha256': 'ff751983662ca34ac0ccca8210846e9eea4ff7d4b575c3d58f5e4827eeb3256f',
               'semantic_certificate_sha256': 'e352f9887e072d7b5097f29b5288c566ce47bbc974387568b544f27d795d1a26',
               'display_receipt_sha256': '22d11ed0d67cf6080f6e93408da8d4d7d2fef67fbe6e22ba6ab9fb16ac677ca2',
               'error_code': None}},
 {'id': 'integer_lcm',
  'expression': 'lcm(6,10,15)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '30',
               'decimal_approximation': '30',
               'display_value': '30',
               'display_mathematical_form': '30',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_LCM(RAT(10/1),RAT(15/1),RAT(6/1))',
               'semantic_canonical': 'RAT(30/1)',
               'structure_certificate_sha256': '2b320f0a539e4233a072ae7c4651cdad9f42766920832f45953d1ad53ab3658c',
               'semantic_certificate_sha256': 'b8e6099bcf79f345e8c21a3389b9107b403871cf677c04a28be092c25d090d50',
               'display_receipt_sha256': 'afcf092375cec6aa20d5788dddbd885d7544b1d31d09845b9296356e551e61d0',
               'error_code': None}},
 {'id': 'integer_power',
  'expression': '2^10',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1024',
               'decimal_approximation': '1024',
               'display_value': '1024',
               'display_mathematical_form': '1024',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(RAT(2/1),RAT(10/1))',
               'semantic_canonical': 'RAT(1024/1)',
               'structure_certificate_sha256': 'b2c979240758c55f955eef1499b79b5e526c017158f1881ae614612cd14c7cfa',
               'semantic_certificate_sha256': 'd0a8444801f08c4c86cf986cefd5dcf0e30bd80ad48af2a63495050e14f2fb7a',
               'display_receipt_sha256': 'a5df955c0f9615a6dfdec720bf99cf78f936cd147827e05e938dffc21c99b6ac',
               'error_code': None}},
 {'id': 'right_associative_power',
  'expression': '2^3^2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '512',
               'decimal_approximation': '512',
               'display_value': '512',
               'display_mathematical_form': '512',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(RAT(2/1),POW(RAT(3/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(512/1)',
               'structure_certificate_sha256': 'eeb20ffecf6b9560f7bcf65c6fc38a7866b480d08c0160e67909d1b226463d5f',
               'semantic_certificate_sha256': '093d04f34c0dc1139400eca975f214ead1d2b273b46f0ca5149bebc33c3cac7d',
               'display_receipt_sha256': '21c2ef7ae4a7dc2bba04c5d2862503f2a517feae1c619abb112cc0931e461370',
               'error_code': None}},
 {'id': 'unary_minus_precedence',
  'expression': '-2^2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '-4',
               'decimal_approximation': '-4',
               'display_value': '-4',
               'display_mathematical_form': '-4',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'UNARY_MINUS(POW(RAT(2/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(-4/1)',
               'structure_certificate_sha256': '7df462a3e7043a0bfd59eb466ad889c57533461dfb267302b9313cf58c043899',
               'semantic_certificate_sha256': 'b236e27a7bcd8a6bf179ebc9909dbafe5c6d159bcd13f864654899401bafc26d',
               'display_receipt_sha256': 'c7f78f38574a3628a3d937a3288603b717863bb5fb9fc0ee51b99cb9ced37008',
               'error_code': None}},
 {'id': 'parenthesized_negative_power',
  'expression': '(-2)^2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '4',
               'decimal_approximation': '4',
               'display_value': '4',
               'display_mathematical_form': '4',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(UNARY_MINUS(RAT(2/1)),RAT(2/1))',
               'semantic_canonical': 'RAT(4/1)',
               'structure_certificate_sha256': '76401746ed2971eb16c6b945127a2a001a10af8bd299f006fe2aa3fb8e574b53',
               'semantic_certificate_sha256': '66fde139e4353c66b4b6bd1e1ea20ae7e88a2f7b4966d6a88b533b294f63f1fb',
               'display_receipt_sha256': '50c157437cee4b30ba6e066a9ef7e9fcdc66a3b73c497ae27cb9415c814b3cc8',
               'error_code': None}},
 {'id': 'negative_exponent',
  'expression': '2^-2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1/4',
               'decimal_approximation': '0.25',
               'display_value': '0.25',
               'display_mathematical_form': '1/4',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(RAT(2/1),UNARY_MINUS(RAT(2/1)))',
               'semantic_canonical': 'RAT(1/4)',
               'structure_certificate_sha256': '59e8674615d365eb49bc3f6032abad5ea5fd4704d8442e3af3e8696c3999ac89',
               'semantic_certificate_sha256': '0d584fce0bca40c14e1e8dcfb224f1f8184363194501acbb03c3e356e5be415e',
               'display_receipt_sha256': '3771b8e63f9236f8e0525e22e77acaacc0a3b61a61d59af932f4ce9a0d98a509',
               'error_code': None}},
 {'id': 'positive_divisor_remainder',
  'expression': '-3 % 2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1',
               'decimal_approximation': '1',
               'display_value': '1',
               'display_mathematical_form': '1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'MOD(UNARY_MINUS(RAT(3/1)),RAT(2/1))',
               'semantic_canonical': 'RAT(1/1)',
               'structure_certificate_sha256': '93bab691505b1da5299e9f09b1828fcb385489a73fdfeeb1b58dc8ea6d81159d',
               'semantic_certificate_sha256': '7198cb7eb85ee7cee6bb638c0c547e07d3584a899a66429d5519bd90b7295d9e',
               'display_receipt_sha256': 'e8c568efa244891d52a1b165fa80cba7caa2cc401fec7be14a5d746e871540d2',
               'error_code': None}},
 {'id': 'negative_divisor_remainder',
  'expression': '3 % -2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '-1',
               'decimal_approximation': '-1',
               'display_value': '-1',
               'display_mathematical_form': '-1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'MOD(RAT(3/1),UNARY_MINUS(RAT(2/1)))',
               'semantic_canonical': 'RAT(-1/1)',
               'structure_certificate_sha256': '297380522721d6c49956da6aff89551b215c6ed6993c6ab86bdfe750c6501960',
               'semantic_certificate_sha256': 'ecd638e867610f01fe6b5e9fab0fd8b3a5afbd24936a7bf0ab1c08175939e2bc',
               'display_receipt_sha256': 'ec2c7fc8400ec7295dfb8a3373b28e8b5c443a338f4779d88e7c3841b28f8993',
               'error_code': None}},
 {'id': 'both_negative_remainder',
  'expression': '-3 % -2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '-1',
               'decimal_approximation': '-1',
               'display_value': '-1',
               'display_mathematical_form': '-1',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'MOD(UNARY_MINUS(RAT(3/1)),UNARY_MINUS(RAT(2/1)))',
               'semantic_canonical': 'RAT(-1/1)',
               'structure_certificate_sha256': 'a30bec3025ca86f98d7e39c590d8a7ae5f1aa729bc9f744ea9bdb7b724b309d8',
               'semantic_certificate_sha256': 'ecd638e867610f01fe6b5e9fab0fd8b3a5afbd24936a7bf0ab1c08175939e2bc',
               'display_receipt_sha256': 'ec2c7fc8400ec7295dfb8a3373b28e8b5c443a338f4779d88e7c3841b28f8993',
               'error_code': None}},
 {'id': 'power_resource_limit',
  'expression': '9^9^9',
  'precision': 30,
  'expected': {'state': 'LIMIT_EXCEEDED',
               'resolution_class': 'LIMITED',
               'display_kind': 'LIMIT_EXCEEDED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'limit exceeded',
               'display_mathematical_form': '9^9^9',
               'display_form_label': 'Submitted expression',
               'structure_canonical': 'POW(RAT(9/1),POW(RAT(9/1),RAT(9/1)))',
               'semantic_canonical': 'LIMIT_EXCEEDED',
               'structure_certificate_sha256': 'e0035344b6528e4b4eb2debf4b24358e0770685ba3c107222ab8d8b3068eaac3',
               'semantic_certificate_sha256': '00f838d7ebd67d2137d9f41021a0400cbb616682daa8e29919c41347d2adf039',
               'display_receipt_sha256': '401f9d162b906b27a4a984480379815afa95844d49508f23361bab4ab97202c3',
               'error_code': 'MAX_EXACT_RESULT_DIGITS'}},
 {'id': 'half_even_round_down',
  'expression': 'round(5/2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '2',
               'decimal_approximation': '2',
               'display_value': '2',
               'display_mathematical_form': '2',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ROUND(DIV(RAT(5/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(2/1)',
               'structure_certificate_sha256': 'b2da4d797b1730977a5e9df5b3bfc773a5f01d43ffa7d06f743982873830cc1b',
               'semantic_certificate_sha256': 'bd09ae09776bfd0376ac1de59e0ba8209249d307a0346a7cbae59ecd7edd5e17',
               'display_receipt_sha256': '47e1693b908fbe62f52fcb4b202ec4452e51321c4a771f47c61f4a459e04fc4b',
               'error_code': None}},
 {'id': 'half_even_round_up',
  'expression': 'round(7/2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '4',
               'decimal_approximation': '4',
               'display_value': '4',
               'display_mathematical_form': '4',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ROUND(DIV(RAT(7/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(4/1)',
               'structure_certificate_sha256': '0ef6bc70abfdcf78886033663f6cd4221f0ac72f76cff34afc976ae6686c7b5c',
               'semantic_certificate_sha256': '66fde139e4353c66b4b6bd1e1ea20ae7e88a2f7b4966d6a88b533b294f63f1fb',
               'display_receipt_sha256': '50c157437cee4b30ba6e066a9ef7e9fcdc66a3b73c497ae27cb9415c814b3cc8',
               'error_code': None}},
 {'id': 'semantic_equivalent_sine_degrees',
  'expression': 'sin(deg(30))',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1/2',
               'decimal_approximation': '0.5',
               'display_value': '0.5',
               'display_mathematical_form': '1/2',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_SIN(CALL_DEG(RAT(30/1)))',
               'semantic_canonical': 'RAT(1/2)',
               'structure_certificate_sha256': '3231e54032fbf00a69c9954afd88449d0333d7842bc55cc86f0afdc3e4a62658',
               'semantic_certificate_sha256': 'ebb862b282b5ce44909f76f40e1146f26a9dddec4af97303276015454c580ada',
               'display_receipt_sha256': 'fd75ee05ad4eb3bfd399f1c246b5170c1abe86bf4de8e43da88ad816f365ffab',
               'error_code': None}},
 {'id': 'semantic_equivalent_fraction',
  'expression': '1/2',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '1/2',
               'decimal_approximation': '0.5',
               'display_value': '0.5',
               'display_mathematical_form': '1/2',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'DIV(RAT(1/1),RAT(2/1))',
               'semantic_canonical': 'RAT(1/2)',
               'structure_certificate_sha256': '3f1f77fc711f71ff770967e235dd094f05676037e5c9e65467125a6a6b324920',
               'semantic_certificate_sha256': 'ebb862b282b5ce44909f76f40e1146f26a9dddec4af97303276015454c580ada',
               'display_receipt_sha256': 'fd75ee05ad4eb3bfd399f1c246b5170c1abe86bf4de8e43da88ad816f365ffab',
               'error_code': None}},
 {'id': 'scientific_resolution_20',
  'expression': 'sin(pi/6) + cos(pi) + sqrt(2) + ln(2)',
  'precision': 20,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': 'ln(2) - 1/2 + sqrt(2)',
               'decimal_approximation': '1.6073607429330403582',
               'display_value': '≈ 1.6073607429330403582',
               'display_mathematical_form': 'ln(2) - 1/2 + sqrt(2)',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'ADD(ADD(ADD(CALL_COS(PI),CALL_SIN(DIV(PI,RAT(6/1)))),CALL_SQRT(RAT(2/1))),CALL_LN(RAT(2/1)))',
               'semantic_canonical': 'ADD(LN(RAT(2/1)),RAT(-1/2),SQRT(RAT(2/1)))',
               'structure_certificate_sha256': '4e1decda8f924cfc8f16285dff84401f656cc006c488f8582ccb56a8daa96572',
               'semantic_certificate_sha256': '6ce0b774132a3f2498c036b2ba1869bc78de283b48f4b27e528842a2e7191f9f',
               'display_receipt_sha256': '27d4b6fa663a5751ef238c1fa7fc90f1f02e0e4ab33fcfed8e2a01ba63ad2a5f',
               'error_code': None}},
 {'id': 'scientific_resolution_30',
  'expression': 'sin(pi/6) + cos(pi) + sqrt(2) + ln(2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': 'ln(2) - 1/2 + sqrt(2)',
               'decimal_approximation': '1.60736074293304035821892084567',
               'display_value': '≈ 1.60736074293304035821892084567',
               'display_mathematical_form': 'ln(2) - 1/2 + sqrt(2)',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'ADD(ADD(ADD(CALL_COS(PI),CALL_SIN(DIV(PI,RAT(6/1)))),CALL_SQRT(RAT(2/1))),CALL_LN(RAT(2/1)))',
               'semantic_canonical': 'ADD(LN(RAT(2/1)),RAT(-1/2),SQRT(RAT(2/1)))',
               'structure_certificate_sha256': '4e1decda8f924cfc8f16285dff84401f656cc006c488f8582ccb56a8daa96572',
               'semantic_certificate_sha256': '6ce0b774132a3f2498c036b2ba1869bc78de283b48f4b27e528842a2e7191f9f',
               'display_receipt_sha256': '62c7b09e5d5b4297291f4e16a66a0957da7d25dd0fc89c73f1278705e165e513',
               'error_code': None}},
 {'id': 'scientific_resolution_60',
  'expression': 'sin(pi/6) + cos(pi) + sqrt(2) + ln(2)',
  'precision': 60,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': 'ln(2) - 1/2 + sqrt(2)',
               'decimal_approximation': '1.60736074293304035821892084566787464664517200973720332729736',
               'display_value': '≈ 1.60736074293304035821892084566787464664517200973720332729736',
               'display_mathematical_form': 'ln(2) - 1/2 + sqrt(2)',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'ADD(ADD(ADD(CALL_COS(PI),CALL_SIN(DIV(PI,RAT(6/1)))),CALL_SQRT(RAT(2/1))),CALL_LN(RAT(2/1)))',
               'semantic_canonical': 'ADD(LN(RAT(2/1)),RAT(-1/2),SQRT(RAT(2/1)))',
               'structure_certificate_sha256': '4e1decda8f924cfc8f16285dff84401f656cc006c488f8582ccb56a8daa96572',
               'semantic_certificate_sha256': '6ce0b774132a3f2498c036b2ba1869bc78de283b48f4b27e528842a2e7191f9f',
               'display_receipt_sha256': '3b6e6df896ade515fddfd8c8eb46c18bc6d39624f9bbabd9ff7e9a9193549620',
               'error_code': None}},
 {'id': 'nesting_resource_limit',
  'expression': '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((1)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))',
  'precision': 30,
  'expected': {'state': 'LIMIT_EXCEEDED',
               'resolution_class': 'LIMITED',
               'display_kind': 'LIMIT_EXCEEDED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'limit exceeded',
               'display_mathematical_form': '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((1)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))',
               'display_form_label': 'Submitted expression',
               'structure_canonical': 'UNRESOLVED',
               'semantic_canonical': 'LIMIT_EXCEEDED',
               'structure_certificate_sha256': '0846961325c1c5586c35cc30d24a305fe5404be3ec3977ab9943d71bcfed272e',
               'semantic_certificate_sha256': '00f838d7ebd67d2137d9f41021a0400cbb616682daa8e29919c41347d2adf039',
               'display_receipt_sha256': 'cacc1d486e1b84e55b9bebc468d4fca0bda617d400d131e3c3c6262a35d660fe',
               'error_code': 'MAX_NESTING_DEPTH'}},
 {'id': 'symbolic_cancel_pi',
  'expression': 'pi - pi',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'SUB(PI,PI)',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': '3800ce17160e097da0e50a31baefaf83a6230b75e6e98ccf53b8e240ef25088b',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'symbolic_cancel_log',
  'expression': 'ln(2) - ln(2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'SUB(CALL_LN(RAT(2/1)),CALL_LN(RAT(2/1)))',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': 'cdaba95b33eee9b7becf312f3be97f7f7bfd600deffccfd0a641ee22d7139139',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'symbolic_cancel_multiple',
  'expression': 'pi + e - pi - e',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'SUB(SUB(ADD(E,PI),PI),E)',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': 'bd924d42a929185e6aed7c5ca7cfc2db95cd2974f6591603d428017a8f2b16f4',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'symbolic_coefficient_reduction',
  'expression': '2*pi - pi',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': 'pi',
               'decimal_approximation': '3.14159265358979323846264338328',
               'display_value': '≈ 3.14159265358979323846264338328',
               'display_mathematical_form': 'pi',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'SUB(MUL(PI,RAT(2/1)),PI)',
               'semantic_canonical': 'PI',
               'structure_certificate_sha256': '24107e7741649ba651cb28c6fab02753eef5427448d99ba5e1f396b9778df50d',
               'semantic_certificate_sha256': '82d249cdca7f75f2c2e36c97cc07dde70e0afbe09e02ca33aca5ee7eda3828e2',
               'display_receipt_sha256': '73c325cdc3512064456b4c924d59d065493203c05b16caf2f25c46fa67eb9a94',
               'error_code': None}},
 {'id': 'symbolic_coefficient_collection',
  'expression': 'sqrt(2) + sqrt(2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_SYMBOLIC',
               'resolution_class': 'EXACT_SYMBOLIC',
               'display_kind': 'APPROXIMATE_SYMBOLIC',
               'exact_value': '2 * sqrt(2)',
               'decimal_approximation': '2.82842712474619009760337744842',
               'display_value': '≈ 2.82842712474619009760337744842',
               'display_mathematical_form': '2 * sqrt(2)',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'ADD(CALL_SQRT(RAT(2/1)),CALL_SQRT(RAT(2/1)))',
               'semantic_canonical': 'MUL(RAT(2/1),SQRT(RAT(2/1)))',
               'structure_certificate_sha256': '46e047341b00869a21dd181bf35b06b9efa76f5884d616edfcefa801ec95ed91',
               'semantic_certificate_sha256': '458d0fa89aa7c42190140164f82457d3b7c9d1759389973852c0392ded5a811a',
               'display_receipt_sha256': 'a2c3b451625a6b20f81ac672803c0810d9407090a351de0af14aab4db2a93d1f',
               'error_code': None}},
 {'id': 'zero_half_power',
  'expression': '0^(1/2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(RAT(0/1),DIV(RAT(1/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': '47f7eacceed0949d52a80ccb4718f215e81fa0a5b68f2844031837d48044c09d',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'zero_three_half_power',
  'expression': '0^(3/2)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'POW(RAT(0/1),DIV(RAT(3/1),RAT(2/1)))',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': '18f1c4a2a5e5f4e6751bcc3a079e7c648c0e0f5e2293c20489a124389e524953',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'zero_negative_half_power',
  'expression': '0^(-1/2)',
  'precision': 30,
  'expected': {'state': 'FORBIDDEN',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNDEFINED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'undefined',
               'display_mathematical_form': '0^(-1/2)',
               'display_form_label': 'Evaluated expression',
               'structure_canonical': 'POW(RAT(0/1),DIV(UNARY_MINUS(RAT(1/1)),RAT(2/1)))',
               'semantic_canonical': 'FORBIDDEN',
               'structure_certificate_sha256': '0d299802a4b0f935500cd0c05efaff5d558173c0977191e9dacbad2fe871e613',
               'semantic_certificate_sha256': '8d3bf4e97e5575ff1bce337df08d2396052ba19bd52bd840581a9ce548d74543',
               'display_receipt_sha256': '89c809e9e20b35ec1596b1377ce7d45b75d962ed0f06605de30cd9674c40db7f',
               'error_code': None}},
 {'id': 'gcd_zero_positive',
  'expression': 'gcd(0,5)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '5',
               'decimal_approximation': '5',
               'display_value': '5',
               'display_mathematical_form': '5',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_GCD(RAT(0/1),RAT(5/1))',
               'semantic_canonical': 'RAT(5/1)',
               'structure_certificate_sha256': 'c40bf07760b5d638ff7cb680157dae96222db065c0ad83d35378ef7db9922a7e',
               'semantic_certificate_sha256': '52defe44059d1a4b4589d2df5057cb8c49f8b00572fa3cf894471276ef73e416',
               'display_receipt_sha256': '8eac9b25d6de30055d48ad784b15b6fe36156b1b681df25463b1a94a335d95e5',
               'error_code': None}},
 {'id': 'gcd_zero_zero',
  'expression': 'gcd(0,0)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_GCD(RAT(0/1),RAT(0/1))',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': '07605559a8f70e8fe735acaeed9088b89fcf5d64477607402698e4e38330fc9b',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'lcm_zero_positive',
  'expression': 'lcm(0,5)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_TERMINATING',
               'exact_value': '0',
               'decimal_approximation': '0',
               'display_value': '0',
               'display_mathematical_form': '0',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_LCM(RAT(0/1),RAT(5/1))',
               'semantic_canonical': 'RAT(0/1)',
               'structure_certificate_sha256': 'd09be977a99bddb305e83e3d945ed065d6d4a0970e439daec6c6bf140e25b258',
               'semantic_certificate_sha256': 'a0d217926a2914fdae3e90f0f8032cae9a8d01abaac348f9c0e7548722b2ca71',
               'display_receipt_sha256': '3d551070b7bc8fd7eba5cd4b93b1057a92d407b1cdb869a7ca6277bc31ed7c3f',
               'error_code': None}},
 {'id': 'repeating_one_third',
  'expression': '1/3',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_REPEATING',
               'exact_value': '1/3',
               'decimal_approximation': '0.3…',
               'display_value': '0.3…',
               'display_mathematical_form': '1/3',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'DIV(RAT(1/1),RAT(3/1))',
               'semantic_canonical': 'RAT(1/3)',
               'structure_certificate_sha256': '35a99012e00510fd940360b86ef01d7ba02644e5b5b80b5c9c6c5d3a0dda83b8',
               'semantic_certificate_sha256': '0614f0485f966508cc98d70fbb3cddfd7b134714d9ddb1dfd9e7610bc4678a00',
               'display_receipt_sha256': 'cd5dfd5c1545b7dfe3eeb293332e19b0563c758661dd495e1e9ad110cb6f2bb5',
               'error_code': None}},
 {'id': 'repeating_one_sixth',
  'expression': '1/6',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_REPEATING',
               'exact_value': '1/6',
               'decimal_approximation': '0.16…',
               'display_value': '0.16…',
               'display_mathematical_form': '1/6',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'DIV(RAT(1/1),RAT(6/1))',
               'semantic_canonical': 'RAT(1/6)',
               'structure_certificate_sha256': '8a08b298831b2913bd9b0427a78a68f4169e4630a0da632c103010521d48bb6b',
               'semantic_certificate_sha256': 'ebae06c8ff7fd306dbcd77ddb8a99e5199488fb00767a30b83bbc43c7bf15d50',
               'display_receipt_sha256': '22c326d123d394670900c61702fd7659fc38569ae6ec6956407fe27683724dcf',
               'error_code': None}},
 {'id': 'repeating_abs_rational',
  'expression': 'abs(-7/3)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_REPEATING',
               'exact_value': '7/3',
               'decimal_approximation': '2.3…',
               'display_value': '2.3…',
               'display_mathematical_form': '7/3',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_ABS(DIV(UNARY_MINUS(RAT(7/1)),RAT(3/1)))',
               'semantic_canonical': 'RAT(7/3)',
               'structure_certificate_sha256': '847a8cd67950770c38d526742e0a4b210862cbce63dfa4dca6c618b7f30ba631',
               'semantic_certificate_sha256': '65ed9427f3baf1eb3b2dd5943f9907087f4b5d7fcc6a4f72795e819c950a7a95',
               'display_receipt_sha256': 'e6f605f04e49cb67c979669ea7bb513ac581c218e62b8f95a65d7df61c29570b',
               'error_code': None}},
 {'id': 'repeating_min_rational',
  'expression': 'min(1/2,1/3)',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_REPEATING',
               'exact_value': '1/3',
               'decimal_approximation': '0.3…',
               'display_value': '0.3…',
               'display_mathematical_form': '1/3',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'CALL_MIN(DIV(RAT(1/1),RAT(2/1)),DIV(RAT(1/1),RAT(3/1)))',
               'semantic_canonical': 'RAT(1/3)',
               'structure_certificate_sha256': '60f3c132c6d28b96f447cbe2fdb37707228b5c8ab27acff0bffcf3d9afc5b3b6',
               'semantic_certificate_sha256': '0614f0485f966508cc98d70fbb3cddfd7b134714d9ddb1dfd9e7610bc4678a00',
               'display_receipt_sha256': 'cd5dfd5c1545b7dfe3eeb293332e19b0563c758661dd495e1e9ad110cb6f2bb5',
               'error_code': None}},
 {'id': 'repeating_mod_rational',
  'expression': '1/2 % 1/3',
  'precision': 30,
  'expected': {'state': 'RESOLVED_EXACT_RATIONAL',
               'resolution_class': 'EXACT_RATIONAL',
               'display_kind': 'EXACT_RATIONAL_REPEATING',
               'exact_value': '1/6',
               'decimal_approximation': '0.16…',
               'display_value': '0.16…',
               'display_mathematical_form': '1/6',
               'display_form_label': 'Exact mathematical form',
               'structure_canonical': 'DIV(MOD(DIV(RAT(1/1),RAT(2/1)),RAT(1/1)),RAT(3/1))',
               'semantic_canonical': 'RAT(1/6)',
               'structure_certificate_sha256': '4829f2ac5995866325ad1b0f655a8239f374be00b8d0aef2b3e8b1c54ebe38b8',
               'semantic_certificate_sha256': 'ebae06c8ff7fd306dbcd77ddb8a99e5199488fb00767a30b83bbc43c7bf15d50',
               'display_receipt_sha256': '22c326d123d394670900c61702fd7659fc38569ae6ec6956407fe27683724dcf',
               'error_code': None}},
 {'id': 'deep_power_tower_limit',
  'expression': '2^2^2^2^2^2',
  'precision': 30,
  'expected': {'state': 'LIMIT_EXCEEDED',
               'resolution_class': 'LIMITED',
               'display_kind': 'LIMIT_EXCEEDED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'limit exceeded',
               'display_mathematical_form': '2^2^2^2^2^2',
               'display_form_label': 'Submitted expression',
               'structure_canonical': 'POW(RAT(2/1),POW(RAT(2/1),POW(RAT(2/1),POW(RAT(2/1),POW(RAT(2/1),RAT(2/1))))))',
               'semantic_canonical': 'LIMIT_EXCEEDED',
               'structure_certificate_sha256': '684dddbabca95d843dfe8500081e8dbf711b3b1d16619e909725577280edb4f1',
               'semantic_certificate_sha256': '00f838d7ebd67d2137d9f41021a0400cbb616682daa8e29919c41347d2adf039',
               'display_receipt_sha256': 'b73a3841a4d8804501ccd7b093c93e8be2d2e816b1ee1ae943650eb93bfbda06',
               'error_code': 'MAX_EXACT_RESULT_DIGITS'}},
 {'id': 'non_ascii_digit_rejection',
  'expression': '١+١',
  'precision': 30,
  'expected': {'state': 'CONFLICT',
               'resolution_class': 'REFUSED',
               'display_kind': 'UNRESOLVED',
               'exact_value': None,
               'decimal_approximation': None,
               'display_value': 'unresolved',
               'display_mathematical_form': '١+١',
               'display_form_label': 'Submitted expression',
               'structure_canonical': 'UNRESOLVED',
               'semantic_canonical': 'CONFLICT',
               'structure_certificate_sha256': '0846961325c1c5586c35cc30d24a305fe5404be3ec3977ab9943d71bcfed272e',
               'semantic_certificate_sha256': 'f2c0cc118b71f230ea80ce439c243c82971e567d7e66db78074d0df474182186',
               'display_receipt_sha256': 'd7983f03c89efabfcb20a3c3e0c54746490639adbc0abb0f9ea1ca1be4ae616d',
               'error_code': 'UNSUPPORTED_CHARACTER'}}]

STATE_EXACT_RATIONAL = "RESOLVED_EXACT_RATIONAL"
STATE_EXACT_SYMBOLIC = "RESOLVED_EXACT_SYMBOLIC"
STATE_FORBIDDEN = "FORBIDDEN"
STATE_INDETERMINATE = "INDETERMINATE"
STATE_SINGULAR = "SINGULAR"
STATE_INCOMPLETE = "INCOMPLETE"
STATE_CONFLICT = "CONFLICT"
STATE_ABSTAIN = "ABSTAIN"
STATE_LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
STATE_INTERNAL_ERROR = "INTERNAL_ERROR"


class ResolutionError(Exception):
    def __init__(self, state: str, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.state = state
        self.message = message
        self.code = code
        self.details = details or {}




@dataclass
class ResolutionBudget:
    remaining: int = MAX_OPERATION_BUDGET

    def consume(self, amount: int = 1) -> None:
        self.remaining -= amount
        if self.remaining < 0:
            raise ResolutionError(
                STATE_LIMIT_EXCEEDED,
                "The expression exceeded the configured operation budget",
                "MAX_OPERATION_BUDGET",
                {"allowed": MAX_OPERATION_BUDGET},
            )


def resource_policy() -> dict:
    return {
        "policy_version": RESOURCE_POLICY_VERSION,
        "max_input_characters": MAX_INPUT_CHARACTERS,
        "max_token_count": MAX_TOKEN_COUNT,
        "max_nesting_depth": MAX_NESTING_DEPTH,
        "max_ast_nodes": MAX_AST_NODES,
        "max_operation_budget": MAX_OPERATION_BUDGET,
        "max_literal_digits": MAX_LITERAL_DIGITS,
        "max_literal_exponent_abs": MAX_LITERAL_EXPONENT_ABS,
        "max_exact_result_digits": MAX_EXACT_RESULT_DIGITS,
    }


def decimal_digit_upper_bound(value: int) -> int:
    value = abs(value)
    if value < 10:
        return 1
    return (value.bit_length() * 30103 + 99999) // 100000 + 1


def enforce_integer_size(value: int, code: str = "MAX_EXACT_RESULT_DIGITS") -> None:
    estimated = decimal_digit_upper_bound(value)
    if estimated > MAX_EXACT_RESULT_DIGITS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The exact integer result exceeds the configured digit limit",
            code,
            {"estimated_digits_upper_bound": estimated, "allowed_digits": MAX_EXACT_RESULT_DIGITS},
        )


def enforce_fraction_size(value: Fraction, code: str = "MAX_EXACT_RESULT_DIGITS") -> None:
    numerator_digits = decimal_digit_upper_bound(value.numerator)
    denominator_digits = decimal_digit_upper_bound(value.denominator)
    estimated = max(numerator_digits, denominator_digits)
    if estimated > MAX_EXACT_RESULT_DIGITS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The exact rational result exceeds the configured digit limit",
            code,
            {
                "estimated_numerator_digits_upper_bound": numerator_digits,
                "estimated_denominator_digits_upper_bound": denominator_digits,
                "allowed_digits": MAX_EXACT_RESULT_DIGITS,
            },
        )


def guard_integer_product(left: int, right: int, message: str = "The exact rational result exceeds the configured digit limit") -> None:
    estimated = decimal_digit_upper_bound(left) + decimal_digit_upper_bound(right)
    if estimated > MAX_EXACT_RESULT_DIGITS + 1:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            message,
            "MAX_EXACT_RESULT_DIGITS",
            {"estimated_digits_upper_bound": estimated, "allowed_digits": MAX_EXACT_RESULT_DIGITS},
        )


def guard_fraction_add(left: Fraction, right: Fraction) -> None:
    guard_integer_product(left.numerator, right.denominator)
    guard_integer_product(right.numerator, left.denominator)
    guard_integer_product(left.denominator, right.denominator)


def guard_fraction_multiply(left: Fraction, right: Fraction) -> None:
    guard_integer_product(left.numerator, right.numerator)
    guard_integer_product(left.denominator, right.denominator)


def preflight_surface(text: str) -> None:
    if len(text) > MAX_INPUT_CHARACTERS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The expression exceeds the configured input-length limit",
            "MAX_INPUT_CHARACTERS",
            {"observed": len(text), "allowed": MAX_INPUT_CHARACTERS},
        )
    depth = 0
    maximum = 0
    for char in text:
        if char == "(":
            depth += 1
            maximum = max(maximum, depth)
            if maximum > MAX_NESTING_DEPTH:
                raise ResolutionError(
                    STATE_LIMIT_EXCEEDED,
                    "The expression exceeds the configured nesting-depth limit",
                    "MAX_NESTING_DEPTH",
                    {"observed": maximum, "allowed": MAX_NESTING_DEPTH},
                )
        elif char == ")":
            depth = max(0, depth - 1)


def count_ast_nodes(root: Node) -> int:
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        if count > MAX_AST_NODES:
            raise ResolutionError(
                STATE_LIMIT_EXCEEDED,
                "The expression exceeds the configured syntax-tree size limit",
                "MAX_AST_NODES",
                {"observed": count, "allowed": MAX_AST_NODES},
            )
        stack.extend(node.args)
    return count


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


@dataclass(frozen=True)
class Node:
    kind: str
    value: str = ""
    args: tuple["Node", ...] = ()


@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    value: Optional[Fraction] = None


@dataclass(frozen=True)
class ResolvedValue:
    state: str
    expr: Optional[Expr]
    note: str


FUNCTION_ARITY = {
    "sqrt": (1, 1),
    "abs": (1, 1),
    "sign": (1, 1),
    "floor": (1, 1),
    "ceil": (1, 1),
    "trunc": (1, 1),
    "round": (1, 1),
    "min": (1, None),
    "max": (1, None),
    "gcd": (2, None),
    "lcm": (2, None),
    "sin": (1, 1),
    "cos": (1, 1),
    "tan": (1, 1),
    "asin": (1, 1),
    "acos": (1, 1),
    "atan": (1, 1),
    "ln": (1, 1),
    "log10": (1, 1),
    "log": (1, 2),
    "exp": (1, 1),
    "deg": (1, 1),
    "rad": (1, 1),
}

CONSTANTS = {"pi", "e", "tau"}
COMMUTATIVE_OPS = {"ADD", "MUL", "MIN", "MAX", "GCD", "LCM"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rat(value: Union[Fraction, int]) -> Expr:
    if not isinstance(value, Fraction):
        value = Fraction(value, 1)
    enforce_fraction_size(value)
    return Expr("RAT", value=value)


def sym(op: str, *args: Expr) -> Expr:
    return Expr(op, tuple(args))


PI = sym("PI")
E_CONST = sym("E")
TAU = sym("TAU")


def is_rat(expr: Expr) -> bool:
    return expr.op == "RAT" and expr.value is not None


def canonical_expr(expr: Expr) -> str:
    if is_rat(expr):
        assert expr.value is not None
        return f"RAT({expr.value.numerator}/{expr.value.denominator})"
    if not expr.args:
        return expr.op
    return f"{expr.op}({','.join(canonical_expr(arg) for arg in expr.args)})"


def pretty_expr(expr: Expr, parent_prec: int = 0) -> str:
    if is_rat(expr):
        assert expr.value is not None
        if expr.value.denominator == 1:
            return str(expr.value.numerator)
        return f"{expr.value.numerator}/{expr.value.denominator}"
    if expr.op == "PI":
        return "pi"
    if expr.op == "E":
        return "e"
    if expr.op == "TAU":
        return "tau"
    if expr.op == "NEG":
        body = pretty_expr(expr.args[0], 40)
        text = f"-{body}"
        return f"({text})" if parent_prec > 40 else text
    if expr.op == "ADD":
        parts = []
        for idx, arg in enumerate(expr.args):
            if arg.op == "NEG":
                parts.append(("- " if idx else "-") + pretty_expr(arg.args[0], 10))
            elif is_rat(arg) and arg.value is not None and arg.value < 0:
                pos = rat(-arg.value)
                parts.append(("- " if idx else "-") + pretty_expr(pos, 10))
            else:
                parts.append(("+ " if idx else "") + pretty_expr(arg, 10))
        text = " ".join(parts)
        return f"({text})" if parent_prec > 10 else text
    if expr.op == "MUL":
        text = " * ".join(pretty_expr(arg, 20) for arg in expr.args)
        return f"({text})" if parent_prec > 20 else text
    if expr.op == "DIV":
        text = f"{pretty_expr(expr.args[0], 20)} / {pretty_expr(expr.args[1], 21)}"
        return f"({text})" if parent_prec > 20 else text
    if expr.op == "MOD":
        text = f"{pretty_expr(expr.args[0], 20)} % {pretty_expr(expr.args[1], 21)}"
        return f"({text})" if parent_prec > 20 else text
    if expr.op == "POW":
        text = f"{pretty_expr(expr.args[0], 30)} ^ {pretty_expr(expr.args[1], 29)}"
        return f"({text})" if parent_prec > 30 else text
    name = expr.op.lower()
    return f"{name}({', '.join(pretty_expr(arg) for arg in expr.args)})"


def normalize_constant(expr: Expr) -> Expr:
    if expr.op == "TAU":
        return make_mul(rat(2), PI)
    return expr


def make_neg(expr: Expr) -> Expr:
    expr = normalize_constant(expr)
    if is_rat(expr):
        assert expr.value is not None
        return rat(-expr.value)
    if expr.op == "NEG":
        return expr.args[0]
    return sym("NEG", expr)


def make_add(*items: Expr) -> Expr:
    rational = Fraction(0, 1)
    grouped: dict[str, tuple[Expr, Fraction]] = {}

    def add_fraction(left: Fraction, right: Fraction) -> Fraction:
        guard_fraction_add(left, right)
        result = left + right
        enforce_fraction_size(result)
        return result

    def split_term(term: Expr) -> tuple[Fraction, Optional[Expr]]:
        term = normalize_constant(term)
        coefficient = Fraction(1, 1)
        if term.op == "NEG":
            coefficient = -coefficient
            term = term.args[0]
        if is_rat(term):
            assert term.value is not None
            return coefficient * term.value, None
        if term.op == "MUL":
            symbolic_args: list[Expr] = []
            for arg in term.args:
                if is_rat(arg):
                    assert arg.value is not None
                    guard_fraction_multiply(coefficient, arg.value)
                    coefficient *= arg.value
                    enforce_fraction_size(coefficient)
                else:
                    symbolic_args.append(arg)
            if not symbolic_args:
                return coefficient, None
            symbolic_args.sort(key=canonical_expr)
            term = symbolic_args[0] if len(symbolic_args) == 1 else sym("MUL", *symbolic_args)
        return coefficient, term

    expanded: list[Expr] = []
    for item in items:
        item = normalize_constant(item)
        expanded.extend(item.args if item.op == "ADD" else (item,))

    for term in expanded:
        coefficient, core = split_term(term)
        if core is None:
            rational = add_fraction(rational, coefficient)
            continue
        key = canonical_expr(core)
        if key in grouped:
            existing_core, existing_coefficient = grouped[key]
            grouped[key] = (existing_core, add_fraction(existing_coefficient, coefficient))
        else:
            grouped[key] = (core, coefficient)

    flat: list[Expr] = []
    for key in sorted(grouped):
        core, coefficient = grouped[key]
        if coefficient == 0:
            continue
        if coefficient == 1:
            flat.append(core)
        elif coefficient == -1:
            flat.append(make_neg(core))
        else:
            flat.append(make_mul(rat(coefficient), core))
    if rational:
        flat.append(rat(rational))
    if not flat:
        return rat(0)
    flat.sort(key=canonical_expr)
    return flat[0] if len(flat) == 1 else sym("ADD", *flat)

def make_mul(*items: Expr) -> Expr:
    flat: list[Expr] = []
    coefficient = Fraction(1, 1)
    for item in items:
        item = normalize_constant(item)
        if item.op == "MUL":
            subitems = item.args
        else:
            subitems = (item,)
        for sub in subitems:
            if is_rat(sub):
                assert sub.value is not None
                guard_fraction_multiply(coefficient, sub.value)
                coefficient *= sub.value
                enforce_fraction_size(coefficient)
            else:
                flat.append(sub)
    if coefficient == 0:
        return rat(0)
    flat.sort(key=canonical_expr)
    if coefficient != 1 or not flat:
        flat.insert(0, rat(coefficient))
    if len(flat) == 1:
        return flat[0]
    return sym("MUL", *flat)


def make_div(left: Expr, right: Expr) -> ResolvedValue:
    left = normalize_constant(left)
    right = normalize_constant(right)
    if is_rat(right) and right.value == 0:
        if is_rat(left) and left.value == 0:
            return ResolvedValue(STATE_INDETERMINATE, None, "Zero divided by Zero has no unique value")
        return ResolvedValue(STATE_FORBIDDEN, None, "Division by Zero is outside the real numeric domain")
    if is_rat(left) and is_rat(right):
        assert left.value is not None and right.value is not None
        guard_integer_product(left.value.numerator, right.value.denominator)
        guard_integer_product(left.value.denominator, right.value.numerator)
        return ResolvedValue(STATE_EXACT_RATIONAL, rat(left.value / right.value), "Exact rational division")
    if is_rat(left) and left.value == 0:
        return ResolvedValue(STATE_EXACT_RATIONAL, rat(0), "Exact Zero")
    if is_rat(right):
        assert right.value is not None
        return resolved_from_expr(make_mul(left, rat(1 / right.value)), "Exact symbolic scaling")
    if canonical_expr(left) == canonical_expr(right):
        return ResolvedValue(STATE_EXACT_RATIONAL, rat(1), "Identical nonzero structures cancel")
    return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("DIV", left, right), "Exact symbolic quotient")


def make_mod(left: Expr, right: Expr) -> ResolvedValue:
    if is_rat(right) and right.value == 0:
        return ResolvedValue(STATE_FORBIDDEN, None, "Modulo by Zero is outside the numeric domain")
    if is_rat(left) and is_rat(right):
        assert left.value is not None and right.value is not None
        q = left.value // right.value
        return ResolvedValue(STATE_EXACT_RATIONAL, rat(left.value - q * right.value), "Exact floor-division remainder")
    return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("MOD", left, right), "Exact symbolic remainder")


def perfect_square_fraction(value: Fraction) -> Optional[Fraction]:
    if value < 0:
        return None
    n = isqrt(value.numerator)
    d = isqrt(value.denominator)
    if n * n == value.numerator and d * d == value.denominator:
        return Fraction(n, d)
    return None


def estimate_power_digits(base: Fraction, exponent: int) -> dict:
    if exponent == 0 or base in {Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)}:
        return {"estimated_numerator_digits_upper_bound": 1, "estimated_denominator_digits_upper_bound": 1}

    magnitude = abs(exponent)
    saturation = MAX_EXACT_RESULT_DIGITS + 1

    def component_estimate(component: int) -> int:
        component = abs(component)
        if component <= 1:
            return 1
        if magnitude > MAX_EXACT_RESULT_DIGITS * 4:
            return saturation
        bits = component.bit_length()
        estimate = (magnitude * bits * 30103 + 99999) // 100000 + 1
        return min(estimate, saturation)

    numerator_digits = component_estimate(base.numerator)
    denominator_digits = component_estimate(base.denominator)
    if exponent < 0:
        numerator_digits, denominator_digits = denominator_digits, numerator_digits
    return {
        "estimated_numerator_digits_upper_bound": numerator_digits,
        "estimated_denominator_digits_upper_bound": denominator_digits,
    }

def enforce_power_size(base: Fraction, exponent: int) -> None:
    estimate = estimate_power_digits(base, exponent)
    if max(estimate.values()) > MAX_EXACT_RESULT_DIGITS:
        public_estimate = {
            key: (f">{MAX_EXACT_RESULT_DIGITS}" if value > MAX_EXACT_RESULT_DIGITS else value)
            for key, value in estimate.items()
        }
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The exact power result exceeds the configured digit limit",
            "MAX_EXACT_RESULT_DIGITS",
            {**public_estimate, "allowed_digits": MAX_EXACT_RESULT_DIGITS},
        )

def make_pow(base: Expr, exponent: Expr) -> ResolvedValue:
    base = normalize_constant(base)
    exponent = normalize_constant(exponent)
    if is_rat(exponent):
        assert exponent.value is not None
        exp_value = exponent.value
        if is_rat(base) and base.value == 0:
            if exp_value == 0:
                return ResolvedValue(STATE_INDETERMINATE, None, "Zero to the Zero power is indeterminate")
            if exp_value < 0:
                return ResolvedValue(STATE_FORBIDDEN, None, "Zero cannot be raised to a negative power")
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(0), "Exact positive power of Zero")
        if exp_value.denominator == 1:
            n = exp_value.numerator
            if n == 0:
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(1), "Exact zero exponent")
            if base.op == "SQRT" and n == 2:
                return resolved_from_expr(base.args[0], "Exact square-root squared identity")
            if is_rat(base):
                assert base.value is not None
                enforce_power_size(base.value, n)
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(base.value ** n), "Exact integer power")
            if n == 1:
                return resolved_from_expr(base, "Identity exponent")
            return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("POW", base, exponent), "Exact symbolic integer power")
        if is_rat(base) and base.value is not None and base.value < 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "A negative real base with a non-integer exponent is outside the real domain")
        if is_rat(base) and base.value is not None and exp_value.denominator == 2:
            root = perfect_square_fraction(base.value)
            if root is not None and exp_value.numerator == 1:
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(root), "Exact square-root power")
    return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("POW", base, exponent), "Exact symbolic power")

def resolved_from_expr(expr: Expr, note: str) -> ResolvedValue:
    expr = normalize_constant(expr)
    state = STATE_EXACT_RATIONAL if is_rat(expr) else STATE_EXACT_SYMBOLIC
    return ResolvedValue(state, expr, note)


def fraction_from_decimal_surface(surface: str) -> Fraction:
    match = re.fullmatch(r"(?:([0-9]+(?:\.[0-9]*)?|\.[0-9]+))(?:[eE]([+-]?[0-9]+))?", surface)
    if not match:
        raise ResolutionError(STATE_CONFLICT, f"Invalid number literal at '{surface}'")
    mantissa = match.group(1)
    exponent_text = match.group(2) or "0"
    unsigned_exponent = exponent_text.lstrip("+-").lstrip("0") or "0"
    if len(unsigned_exponent) > 6:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The numeric literal exponent exceeds the configured limit",
            "MAX_LITERAL_EXPONENT_ABS",
            {"allowed": MAX_LITERAL_EXPONENT_ABS},
        )
    exponent = int(exponent_text)
    if abs(exponent) > MAX_LITERAL_EXPONENT_ABS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The numeric literal exponent exceeds the configured limit",
            "MAX_LITERAL_EXPONENT_ABS",
            {"observed": abs(exponent), "allowed": MAX_LITERAL_EXPONENT_ABS},
        )
    if "." in mantissa:
        left, right = mantissa.split(".", 1)
    else:
        left, right = mantissa, ""
    left = left or "0"
    digits = (left + right).lstrip("0") or "0"
    if len(digits) > MAX_LITERAL_DIGITS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The numeric literal exceeds the configured digit limit",
            "MAX_LITERAL_DIGITS",
            {"observed": len(digits), "allowed": MAX_LITERAL_DIGITS},
        )
    decimal_shift = exponent - len(right)
    estimated_numerator_digits = len(digits) + max(0, decimal_shift)
    estimated_denominator_digits = max(1, -decimal_shift + 1)
    if max(estimated_numerator_digits, estimated_denominator_digits) > MAX_EXACT_RESULT_DIGITS:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The exact value represented by the numeric literal exceeds the configured digit limit",
            "MAX_EXACT_RESULT_DIGITS",
            {
                "estimated_numerator_digits": estimated_numerator_digits,
                "estimated_denominator_digits": estimated_denominator_digits,
                "allowed_digits": MAX_EXACT_RESULT_DIGITS,
            },
        )
    value = Fraction(int(digits), 10 ** len(right))
    if exponent >= 0:
        value *= 10 ** exponent
    else:
        value /= 10 ** (-exponent)
    enforce_fraction_size(value)
    return value


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    idx = 0
    while idx < len(text):
        ch = text[idx]
        if ch.isspace():
            idx += 1
            continue
        if text.startswith("**", idx):
            tokens.append(Token("POW", "**", idx))
            idx += 2
            continue
        if ch in "+-*/%^(),":
            kind = "POW" if ch == "^" else ch
            tokens.append(Token(kind, ch, idx))
            idx += 1
            continue
        number_match = re.match(r"(?:(?:[0-9]+(?:\.[0-9]*)?)|(?:\.[0-9]+))(?:[eE][+-]?[0-9]+)?", text[idx:])
        if number_match:
            raw = number_match.group(0)
            tokens.append(Token("NUMBER", raw, idx))
            idx += len(raw)
            continue
        name_match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text[idx:])
        if name_match:
            raw = name_match.group(0)
            tokens.append(Token("NAME", raw.lower(), idx))
            idx += len(raw)
            continue
        raise ResolutionError(STATE_CONFLICT, f"Unsupported token '{ch}' at position {idx}", "UNSUPPORTED_CHARACTER")
        
    if len(tokens) > MAX_TOKEN_COUNT:
        raise ResolutionError(
            STATE_LIMIT_EXCEEDED,
            "The expression exceeds the configured token-count limit",
            "MAX_TOKEN_COUNT",
            {"observed": len(tokens), "allowed": MAX_TOKEN_COUNT},
        )
    tokens.append(Token("EOF", "", len(text)))
    return tokens


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def current(self) -> Token:
        return self.tokens[self.index]

    def take(self, kind: Optional[str] = None) -> Token:
        token = self.current()
        if kind is not None and token.kind != kind:
            if token.kind == "EOF":
                raise ResolutionError(STATE_INCOMPLETE, f"Expected {kind} before the expression ended")
            raise ResolutionError(STATE_CONFLICT, f"Expected {kind} at position {token.position}")
        self.index += 1
        return token

    def parse(self) -> Node:
        if self.current().kind == "EOF":
            raise ResolutionError(STATE_INCOMPLETE, "Expression is empty")
        node = self.parse_add()
        if self.current().kind != "EOF":
            token = self.current()
            raise ResolutionError(STATE_CONFLICT, f"Unexpected token '{token.value}' at position {token.position}")
        return node

    def parse_add(self) -> Node:
        node = self.parse_mul()
        while self.current().kind in {"+", "-"}:
            op = self.take().kind
            node = Node("binary", op, (node, self.parse_mul()))
        return node

    def parse_mul(self) -> Node:
        node = self.parse_unary()
        while self.current().kind in {"*", "/", "%"}:
            op = self.take().kind
            node = Node("binary", op, (node, self.parse_unary()))
        return node

    def parse_power(self) -> Node:
        node = self.parse_primary()
        if self.current().kind == "POW":
            self.take("POW")
            node = Node("binary", "^", (node, self.parse_unary()))
        return node

    def parse_unary(self) -> Node:
        if self.current().kind in {"+", "-"}:
            op = self.take().kind
            return Node("unary", op, (self.parse_unary(),))
        return self.parse_power()

    def parse_primary(self) -> Node:
        token = self.current()
        if token.kind == "NUMBER":
            self.take("NUMBER")
            return Node("number", token.value)
        if token.kind == "NAME":
            self.take("NAME")
            name = token.value
            if self.current().kind == "(":
                self.take("(")
                args: list[Node] = []
                if self.current().kind != ")":
                    args.append(self.parse_add())
                    while self.current().kind == ",":
                        self.take(",")
                        args.append(self.parse_add())
                if self.current().kind != ")":
                    if self.current().kind == "EOF":
                        raise ResolutionError(STATE_INCOMPLETE, f"Function '{name}' is missing a closing parenthesis")
                    raise ResolutionError(STATE_CONFLICT, f"Function '{name}' has an invalid argument structure")
                self.take(")")
                return Node("call", name, tuple(args))
            return Node("name", name)
        if token.kind == "(":
            self.take("(")
            node = self.parse_add()
            if self.current().kind != ")":
                if self.current().kind == "EOF":
                    raise ResolutionError(STATE_INCOMPLETE, "Grouped expression is missing a closing parenthesis")
                raise ResolutionError(STATE_CONFLICT, "Grouped expression is malformed")
            self.take(")")
            return node
        if token.kind == "EOF":
            raise ResolutionError(STATE_INCOMPLETE, "Expression ended before a value was supplied")
        raise ResolutionError(STATE_CONFLICT, f"Invalid expression at position {token.position}")


def canonical_node(node: Node) -> str:
    if node.kind == "number":
        value = fraction_from_decimal_surface(node.value)
        return f"RAT({value.numerator}/{value.denominator})"
    if node.kind == "name":
        return node.value.upper()
    if node.kind == "unary":
        return f"UNARY_{'PLUS' if node.value == '+' else 'MINUS'}({canonical_node(node.args[0])})"
    if node.kind == "binary":
        op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD", "^": "POW"}
        left = canonical_node(node.args[0])
        right = canonical_node(node.args[1])
        op = op_map[node.value]
        if op in {"ADD", "MUL"}:
            left, right = sorted((left, right))
        return f"{op}({left},{right})"
    if node.kind == "call":
        args = [canonical_node(arg) for arg in node.args]
        if node.value.upper() in COMMUTATIVE_OPS:
            args.sort()
        return f"CALL_{node.value.upper()}({','.join(args)})"
    raise ResolutionError(STATE_CONFLICT, "Unknown structural node")


def is_integer_fraction(value: Fraction) -> bool:
    return value.denominator == 1


def integer_power_of_ten(value: int) -> Optional[int]:
    if value <= 0:
        return None
    power = 0
    while value % 10 == 0:
        value //= 10
        power += 1
    return power if value == 1 else None


def rational_power_of_ten(value: Fraction) -> Optional[int]:
    if value <= 0:
        return None
    top = integer_power_of_ten(value.numerator)
    bottom = integer_power_of_ten(value.denominator)
    if top is None or bottom is None:
        return None
    return top - bottom


def extract_pi_multiple(expr: Expr) -> Optional[Fraction]:
    expr = normalize_constant(expr)
    if expr.op == "PI":
        return Fraction(1, 1)
    if expr.op == "NEG":
        inner = extract_pi_multiple(expr.args[0])
        return -inner if inner is not None else None
    if expr.op == "MUL":
        coefficient = Fraction(1, 1)
        pi_count = 0
        for arg in expr.args:
            if is_rat(arg):
                assert arg.value is not None
                coefficient *= arg.value
            elif arg.op == "PI":
                pi_count += 1
            else:
                return None
        if pi_count == 1:
            return coefficient
    return None


def sqrt_symbolic_int(n: int) -> Expr:
    root = isqrt(n)
    if root * root == n:
        return rat(root)
    return sym("SQRT", rat(n))


def trig_base_values(index: int) -> tuple[Expr, Expr, Optional[Expr]]:
    s2 = sqrt_symbolic_int(2)
    s3 = sqrt_symbolic_int(3)
    s6 = sqrt_symbolic_int(6)
    sin_base = {
        0: rat(0),
        1: make_div(make_add(s6, make_neg(s2)), rat(4)).expr,
        2: rat(Fraction(1, 2)),
        3: make_div(s2, rat(2)).expr,
        4: make_div(s3, rat(2)).expr,
        5: make_div(make_add(s6, s2), rat(4)).expr,
        6: rat(1),
    }
    cos_base = {
        0: rat(1),
        1: make_div(make_add(s6, s2), rat(4)).expr,
        2: make_div(s3, rat(2)).expr,
        3: make_div(s2, rat(2)).expr,
        4: rat(Fraction(1, 2)),
        5: make_div(make_add(s6, make_neg(s2)), rat(4)).expr,
        6: rat(0),
    }
    tan_base = {
        0: rat(0),
        1: make_add(rat(2), make_neg(s3)),
        2: make_div(s3, rat(3)).expr,
        3: rat(1),
        4: s3,
        5: make_add(rat(2), s3),
        6: None,
    }
    return sin_base[index], cos_base[index], tan_base[index]


def exact_trig(name: str, coefficient: Fraction) -> Optional[ResolvedValue]:
    scaled = coefficient * 12
    if scaled.denominator != 1:
        return None
    k = scaled.numerator % 24
    quadrant = k // 6
    offset = k % 6
    if quadrant == 0:
        base_idx = offset
        sin_sign, cos_sign, tan_sign = 1, 1, 1
    elif quadrant == 1:
        base_idx = 6 - offset
        sin_sign, cos_sign, tan_sign = 1, -1, -1
    elif quadrant == 2:
        base_idx = offset
        sin_sign, cos_sign, tan_sign = -1, -1, 1
    else:
        base_idx = 6 - offset
        sin_sign, cos_sign, tan_sign = -1, 1, -1
    sin_value, cos_value, tan_value = trig_base_values(base_idx)
    if name == "sin":
        expr = sin_value if sin_sign > 0 else make_neg(sin_value)
        return resolved_from_expr(expr, "Exact common-angle sine identity")
    if name == "cos":
        expr = cos_value if cos_sign > 0 else make_neg(cos_value)
        return resolved_from_expr(expr, "Exact common-angle cosine identity")
    if tan_value is None:
        return ResolvedValue(STATE_SINGULAR, None, "Tangent is singular where cosine is zero")
    expr = tan_value if tan_sign > 0 else make_neg(tan_value)
    return resolved_from_expr(expr, "Exact common-angle tangent identity")


def expr_matches(left: Expr, right: Expr) -> bool:
    return canonical_expr(left) == canonical_expr(right)


def exact_inverse_trig(name: str, argument: Expr) -> Optional[ResolvedValue]:
    candidates: list[tuple[Fraction, Expr, Expr, Expr]] = []
    for k in range(0, 7):
        angle = Fraction(k, 12)
        s, c, t = trig_base_values(k)
        angle_expr = make_mul(rat(angle), PI)
        candidates.append((angle, s, c, t if t is not None else sym("UNDEFINED")))
    if name == "asin":
        for angle, s, _, _ in candidates:
            if expr_matches(argument, s):
                return resolved_from_expr(make_mul(rat(angle), PI), "Exact inverse-sine identity")
            if expr_matches(argument, make_neg(s)):
                return resolved_from_expr(make_neg(make_mul(rat(angle), PI)), "Exact inverse-sine identity")
    if name == "acos":
        for angle, _, c, _ in candidates:
            if expr_matches(argument, c):
                return resolved_from_expr(make_mul(rat(angle), PI), "Exact inverse-cosine identity")
            if expr_matches(argument, make_neg(c)):
                return resolved_from_expr(make_mul(rat(1 - angle), PI), "Exact inverse-cosine identity")
    if name == "atan":
        for angle, _, _, t in candidates:
            if t.op == "UNDEFINED":
                continue
            if expr_matches(argument, t):
                return resolved_from_expr(make_mul(rat(angle), PI), "Exact inverse-tangent identity")
            if expr_matches(argument, make_neg(t)):
                return resolved_from_expr(make_neg(make_mul(rat(angle), PI)), "Exact inverse-tangent identity")
    return None


def known_sign(expr: Expr) -> Optional[int]:
    expr = normalize_constant(expr)
    if is_rat(expr):
        assert expr.value is not None
        return 0 if expr.value == 0 else (1 if expr.value > 0 else -1)
    if expr.op in {"PI", "E", "TAU", "EXP"}:
        return 1
    if expr.op == "NEG":
        sign = known_sign(expr.args[0])
        return None if sign is None else -sign
    if expr.op == "ABS":
        sign = known_sign(expr.args[0])
        return 0 if sign == 0 else 1
    if expr.op == "SQRT":
        sign = known_sign(expr.args[0])
        return 0 if sign == 0 else 1
    if expr.op == "LN":
        arg = expr.args[0]
        if is_rat(arg) and arg.value is not None:
            return 0 if arg.value == 1 else (1 if arg.value > 1 else -1)
        if arg.op == "E":
            return 1
        if arg.op == "EXP":
            return known_sign(arg.args[0])
    if expr.op == "LOG10":
        arg = expr.args[0]
        if is_rat(arg) and arg.value is not None:
            return 0 if arg.value == 1 else (1 if arg.value > 1 else -1)
    if expr.op == "MUL":
        result = 1
        for arg in expr.args:
            sign = known_sign(arg)
            if sign is None:
                return None
            if sign == 0:
                return 0
            result *= sign
        return result
    if expr.op == "DIV":
        left = known_sign(expr.args[0])
        right = known_sign(expr.args[1])
        if left is None or right in {None, 0}:
            return None
        return 0 if left == 0 else left * right
    if expr.op == "POW" and is_rat(expr.args[1]) and expr.args[1].value is not None:
        exponent = expr.args[1].value
        base_sign = known_sign(expr.args[0])
        if exponent.denominator == 1 and base_sign is not None:
            n = exponent.numerator
            if n == 0:
                return 1
            if base_sign == 0:
                return 0 if n > 0 else None
            return 1 if n % 2 == 0 else base_sign
    return None


def call_function(name: str, args: list[Expr]) -> ResolvedValue:
    if name not in FUNCTION_ARITY:
        return ResolvedValue(STATE_ABSTAIN, None, f"Function '{name}' is not in the SVARE v{VERSION} bounded function registry")
    minimum, maximum = FUNCTION_ARITY[name]
    if len(args) < minimum or (maximum is not None and len(args) > maximum):
        expected = str(minimum) if maximum == minimum else f"{minimum}..{maximum if maximum is not None else 'n'}"
        return ResolvedValue(STATE_CONFLICT, None, f"Function '{name}' expects {expected} argument(s), received {len(args)}")

    if name == "sqrt":
        arg = args[0]
        sign = known_sign(arg)
        if sign is not None and sign < 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "Square root of a negative value is outside the real domain")
        if sign == 0:
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(0), "Exact square root of Zero")
        if is_rat(arg):
            assert arg.value is not None
            root = perfect_square_fraction(arg.value)
            if root is not None:
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(root), "Exact rational square root")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("SQRT", arg), "Exact symbolic square root")

    if name == "abs":
        arg = args[0]
        if is_rat(arg):
            assert arg.value is not None
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(abs(arg.value)), "Exact absolute value")
        if arg.op == "NEG":
            return resolved_from_expr(arg.args[0], "Exact absolute-value simplification")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("ABS", arg), "Exact symbolic absolute value")

    if name == "sign":
        arg = args[0]
        if is_rat(arg):
            assert arg.value is not None
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(0 if arg.value == 0 else (1 if arg.value > 0 else -1)), "Exact sign")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("SIGN", arg), "Exact symbolic sign")

    if name in {"floor", "ceil", "trunc", "round"}:
        arg = args[0]
        if is_rat(arg):
            assert arg.value is not None
            value = arg.value
            if name == "floor":
                result = value.numerator // value.denominator
            elif name == "ceil":
                result = -((-value.numerator) // value.denominator)
            elif name == "trunc":
                result = abs(value.numerator) // value.denominator
                if value < 0:
                    result = -result
            else:
                lower = value.numerator // value.denominator
                remainder = value - lower
                if remainder < Fraction(1, 2):
                    result = lower
                elif remainder > Fraction(1, 2):
                    result = lower + 1
                else:
                    result = lower if lower % 2 == 0 else lower + 1
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(result), f"Exact {name} result")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym(name.upper(), arg), f"Exact symbolic {name}")

    if name in {"min", "max"}:
        if all(is_rat(arg) for arg in args):
            values = [arg.value for arg in args]
            assert all(value is not None for value in values)
            selected = min(values) if name == "min" else max(values)
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(selected), f"Exact {name} result")
        ordered = sorted(args, key=canonical_expr)
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym(name.upper(), *ordered), f"Exact symbolic {name}")

    if name in {"gcd", "lcm"}:
        if not all(is_rat(arg) and arg.value is not None and is_integer_fraction(arg.value) for arg in args):
            return ResolvedValue(STATE_FORBIDDEN, None, f"{name} requires integer arguments")
        numbers = [abs(arg.value.numerator) for arg in args if arg.value is not None]
        if name == "gcd":
            result = 0
            for number in numbers:
                result = gcd(result, number)
        else:
            result = 1
            for number in numbers:
                if result == 0 or number == 0:
                    result = 0
                else:
                    common = gcd(result, number)
                    reduced = result // common
                    estimated = decimal_digit_upper_bound(reduced) + decimal_digit_upper_bound(number)
                    if estimated > MAX_EXACT_RESULT_DIGITS + 1:
                        raise ResolutionError(
                            STATE_LIMIT_EXCEEDED,
                            "The exact lcm result exceeds the configured digit limit",
                            "MAX_EXACT_RESULT_DIGITS",
                            {"estimated_digits_upper_bound": estimated, "allowed_digits": MAX_EXACT_RESULT_DIGITS},
                        )
                    result = abs(reduced * number)
                    enforce_integer_size(result)
        return ResolvedValue(STATE_EXACT_RATIONAL, rat(result), f"Exact integer {name}")

    if name == "deg":
        return resolved_from_expr(make_mul(args[0], rat(Fraction(1, 180)), PI), "Degrees converted exactly to radians")

    if name == "rad":
        return resolved_from_expr(args[0], "Radians preserve the supplied angle")

    if name in {"sin", "cos", "tan"}:
        coefficient = extract_pi_multiple(args[0])
        if coefficient is not None:
            exact = exact_trig(name, coefficient)
            if exact is not None:
                return exact
        if is_rat(args[0]) and args[0].value == 0:
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(0 if name != "cos" else 1), f"Exact {name} at Zero")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym(name.upper(), args[0]), f"Exact symbolic {name}")

    if name in {"asin", "acos", "atan"}:
        arg = args[0]
        if name in {"asin", "acos"} and is_rat(arg):
            assert arg.value is not None
            if arg.value < -1 or arg.value > 1:
                return ResolvedValue(STATE_FORBIDDEN, None, f"{name} requires an argument in [-1, 1] in the real domain")
        exact = exact_inverse_trig(name, arg)
        if exact is not None:
            return exact
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym(name.upper(), arg), f"Exact symbolic {name}")

    if name == "ln":
        arg = args[0]
        sign = known_sign(arg)
        if sign is not None and sign <= 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "Natural logarithm requires a positive real argument")
        if is_rat(arg):
            assert arg.value is not None
            if arg.value == 1:
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(0), "Exact natural logarithm identity")
        if arg.op == "E":
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(1), "Exact natural logarithm identity")
        if arg.op == "POW" and arg.args[0].op == "E":
            return resolved_from_expr(arg.args[1], "Exact ln(exp(x)) identity")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("LN", arg), "Exact symbolic natural logarithm")

    if name == "log10":
        arg = args[0]
        sign = known_sign(arg)
        if sign is not None and sign <= 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "Base-10 logarithm requires a positive real argument")
        if is_rat(arg):
            assert arg.value is not None
            power = rational_power_of_ten(arg.value)
            if power is not None:
                return ResolvedValue(STATE_EXACT_RATIONAL, rat(power), "Exact power-of-ten logarithm")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("LOG10", arg), "Exact symbolic base-10 logarithm")

    if name == "log":
        if len(args) == 1:
            return call_function("ln", args)
        value, base = args
        value_sign = known_sign(value)
        base_sign = known_sign(base)
        if value_sign is not None and value_sign <= 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "Logarithm requires a positive real value")
        if base_sign is not None and base_sign <= 0:
            return ResolvedValue(STATE_FORBIDDEN, None, "Logarithm base must be positive and not equal to 1")
        if is_rat(base) and base.value is not None and base.value == 1:
            return ResolvedValue(STATE_FORBIDDEN, None, "Logarithm base must be positive and not equal to 1")
        if (
            is_rat(value)
            and is_rat(base)
            and value.value is not None
            and base.value is not None
            and max(
                decimal_digit_upper_bound(value.value.numerator),
                decimal_digit_upper_bound(value.value.denominator),
                decimal_digit_upper_bound(base.value.numerator),
                decimal_digit_upper_bound(base.value.denominator),
            ) <= 128
        ):
            for exponent in range(-64, 65):
                if base.value ** exponent == value.value:
                    return ResolvedValue(STATE_EXACT_RATIONAL, rat(exponent), "Exact logarithm power identity")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("LOG", value, base), "Exact symbolic logarithm")

    if name == "exp":
        arg = args[0]
        if is_rat(arg) and arg.value == 0:
            return ResolvedValue(STATE_EXACT_RATIONAL, rat(1), "Exact exponential identity")
        if arg.op == "LN":
            return resolved_from_expr(arg.args[0], "Exact exp(ln(x)) identity")
        if is_rat(arg) and arg.value == 1:
            return ResolvedValue(STATE_EXACT_SYMBOLIC, E_CONST, "Exact constant e")
        return ResolvedValue(STATE_EXACT_SYMBOLIC, sym("EXP", arg), "Exact symbolic exponential")

    return ResolvedValue(STATE_ABSTAIN, None, f"Function '{name}' is not implemented")


def evaluate(node: Node, records: list[dict], budget: ResolutionBudget) -> ResolvedValue:
    budget.consume()
    if node.kind == "number":
        result = ResolvedValue(STATE_EXACT_RATIONAL, rat(fraction_from_decimal_surface(node.value)), "Exact decimal-to-rational parsing")
    elif node.kind == "name":
        if node.value == "pi":
            result = ResolvedValue(STATE_EXACT_SYMBOLIC, PI, "Exact symbolic constant pi")
        elif node.value == "e":
            result = ResolvedValue(STATE_EXACT_SYMBOLIC, E_CONST, "Exact symbolic constant e")
        elif node.value == "tau":
            result = ResolvedValue(STATE_EXACT_SYMBOLIC, TAU, "Exact symbolic constant tau")
        else:
            result = ResolvedValue(STATE_ABSTAIN, None, f"Unbound name '{node.value}'")
    elif node.kind == "unary":
        child = evaluate(node.args[0], records, budget)
        if child.expr is None:
            result = child
        elif node.value == "+":
            result = resolved_from_expr(child.expr, "Unary plus preserves the value")
        else:
            result = resolved_from_expr(make_neg(child.expr), "Exact unary negation")
    elif node.kind == "binary":
        left = evaluate(node.args[0], records, budget)
        if left.expr is None:
            result = left
        else:
            right = evaluate(node.args[1], records, budget)
            if right.expr is None:
                result = right
            elif node.value == "+":
                result = resolved_from_expr(make_add(left.expr, right.expr), "Exact addition")
            elif node.value == "-":
                result = resolved_from_expr(make_add(left.expr, make_neg(right.expr)), "Exact subtraction")
            elif node.value == "*":
                result = resolved_from_expr(make_mul(left.expr, right.expr), "Exact multiplication")
            elif node.value == "/":
                result = make_div(left.expr, right.expr)
            elif node.value == "%":
                result = make_mod(left.expr, right.expr)
            else:
                result = make_pow(left.expr, right.expr)
    elif node.kind == "call":
        evaluated: list[Expr] = []
        terminal: Optional[ResolvedValue] = None
        for arg in node.args:
            value = evaluate(arg, records, budget)
            if value.expr is None:
                terminal = value
                break
            evaluated.append(value.expr)
        result = terminal if terminal is not None else call_function(node.value, evaluated)
    else:
        result = ResolvedValue(STATE_CONFLICT, None, "Unknown expression node")

    records.append(
        {
            "node": canonical_node(node),
            "state": result.state,
            "exact": pretty_expr(result.expr) if result.expr is not None else None,
            "note": result.note,
        }
    )
    return result


def decimal_pi(precision: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision + 10
        c = Decimal(426880) * Decimal(10005).sqrt()
        m = 1
        l = 13591409
        x = 1
        k = 6
        series = Decimal(l)
        terms = max(2, precision // 14 + 2)
        for i in range(1, terms):
            m = (m * (k**3 - 16 * k)) // (i**3)
            l += 545140134
            x *= -262537412640768000
            series += Decimal(m * l) / Decimal(x)
            k += 12
        return +(c / series)


def decimal_sin(value: Decimal, precision: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision + 10
        pi = decimal_pi(ctx.prec)
        two_pi = pi * 2
        value = value % two_pi
        if value > pi:
            value -= two_pi
        if value < -pi:
            value += two_pi
        if value > pi / 2:
            value = pi - value
        elif value < -pi / 2:
            value = -pi - value
        term = value
        total = value
        n = 1
        threshold = Decimal(10) ** (-(precision + 5))
        while abs(term) > threshold and n < 10000:
            term *= -(value * value) / Decimal((2 * n) * (2 * n + 1))
            total += term
            n += 1
        return +total


def decimal_cos(value: Decimal, precision: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision + 10
        pi = decimal_pi(ctx.prec)
        two_pi = pi * 2
        value = value % two_pi
        if value > pi:
            value -= two_pi
        if value < -pi:
            value += two_pi
        sign = Decimal(1)
        if value > pi / 2:
            value = pi - value
            sign = Decimal(-1)
        elif value < -pi / 2:
            value = -pi - value
            sign = Decimal(-1)
        term = Decimal(1)
        total = Decimal(1)
        n = 1
        threshold = Decimal(10) ** (-(precision + 5))
        while abs(term) > threshold and n < 10000:
            term *= -(value * value) / Decimal((2 * n - 1) * (2 * n))
            total += term
            n += 1
        return +(sign * total)


def decimal_atan(value: Decimal, precision: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision + 12
        pi = decimal_pi(ctx.prec)
        if value < 0:
            return -decimal_atan(-value, precision)
        if value > 1:
            return +(pi / 2 - decimal_atan(Decimal(1) / value, precision))
        if value > Decimal("0.5"):
            return +(pi / 4 + decimal_atan((value - 1) / (value + 1), precision))
        term = value
        total = value
        square = value * value
        n = 1
        threshold = Decimal(10) ** (-(precision + 6))
        while abs(term) > threshold and n < 100000:
            term *= -square
            total += term / Decimal(2 * n + 1)
            n += 1
        return +total


def eval_decimal(expr: Expr, precision: int) -> Decimal:
    work_precision = precision + 24
    memo: dict[str, Decimal] = {}

    def evaluate_decimal(node: Expr) -> Decimal:
        key = canonical_expr(node)
        cached = memo.get(key)
        if cached is not None:
            return cached
        if is_rat(node):
            assert node.value is not None
            value = Decimal(node.value.numerator) / Decimal(node.value.denominator)
        elif node.op == "PI":
            value = decimal_pi(work_precision)
        elif node.op == "E":
            value = Decimal(1).exp()
        elif node.op == "TAU":
            value = decimal_pi(work_precision) * 2
        elif node.op == "NEG":
            value = -evaluate_decimal(node.args[0])
        elif node.op == "ADD":
            value = sum((evaluate_decimal(arg) for arg in node.args), Decimal(0))
        elif node.op == "MUL":
            value = Decimal(1)
            for arg in node.args:
                value *= evaluate_decimal(arg)
        elif node.op == "DIV":
            denominator = evaluate_decimal(node.args[1])
            if denominator == 0:
                raise ResolutionError(STATE_SINGULAR, "Decimal approximation encountered a Zero denominator")
            value = evaluate_decimal(node.args[0]) / denominator
        elif node.op == "MOD":
            left = evaluate_decimal(node.args[0])
            right = evaluate_decimal(node.args[1])
            value = left % right
        elif node.op == "POW":
            base = evaluate_decimal(node.args[0])
            exponent = evaluate_decimal(node.args[1])
            if is_rat(node.args[1]) and node.args[1].value is not None and node.args[1].value.denominator == 1:
                value = base ** node.args[1].value.numerator
            else:
                if base <= 0:
                    raise ResolutionError(STATE_FORBIDDEN, "Decimal non-integer power requires a positive base in the real domain")
                value = (exponent * base.ln()).exp()
        elif node.op == "SQRT":
            argument = evaluate_decimal(node.args[0])
            if argument < 0:
                raise ResolutionError(STATE_FORBIDDEN, "Square root is outside the real domain")
            value = argument.sqrt()
        elif node.op == "ABS":
            value = abs(evaluate_decimal(node.args[0]))
        elif node.op == "SIGN":
            argument = evaluate_decimal(node.args[0])
            value = Decimal(0 if argument == 0 else (1 if argument > 0 else -1))
        elif node.op == "FLOOR":
            value = evaluate_decimal(node.args[0]).to_integral_value(rounding="ROUND_FLOOR")
        elif node.op == "CEIL":
            value = evaluate_decimal(node.args[0]).to_integral_value(rounding="ROUND_CEILING")
        elif node.op == "TRUNC":
            value = evaluate_decimal(node.args[0]).to_integral_value(rounding="ROUND_DOWN")
        elif node.op == "ROUND":
            value = evaluate_decimal(node.args[0]).to_integral_value(rounding="ROUND_HALF_EVEN")
        elif node.op == "MIN":
            value = min(evaluate_decimal(arg) for arg in node.args)
        elif node.op == "MAX":
            value = max(evaluate_decimal(arg) for arg in node.args)
        elif node.op in {"GCD", "LCM"}:
            raise ResolutionError(STATE_ABSTAIN, "Symbolic gcd/lcm approximation is not supported")
        elif node.op == "SIN":
            value = decimal_sin(evaluate_decimal(node.args[0]), work_precision)
        elif node.op == "COS":
            value = decimal_cos(evaluate_decimal(node.args[0]), work_precision)
        elif node.op == "TAN":
            angle = evaluate_decimal(node.args[0])
            cosine = decimal_cos(angle, work_precision)
            threshold = Decimal(10) ** (-(precision + 2))
            if abs(cosine) <= threshold:
                raise ResolutionError(STATE_SINGULAR, "Tangent is singular at this angle")
            value = decimal_sin(angle, work_precision) / cosine
        elif node.op == "ASIN":
            argument = evaluate_decimal(node.args[0])
            if argument < -1 or argument > 1:
                raise ResolutionError(STATE_FORBIDDEN, "asin requires a value in [-1, 1]")
            if argument == 1:
                value = decimal_pi(work_precision) / 2
            elif argument == -1:
                value = -decimal_pi(work_precision) / 2
            else:
                value = decimal_atan(argument / (Decimal(1) - argument * argument).sqrt(), work_precision)
        elif node.op == "ACOS":
            argument = evaluate_decimal(node.args[0])
            if argument < -1 or argument > 1:
                raise ResolutionError(STATE_FORBIDDEN, "acos requires a value in [-1, 1]")
            asin_value = evaluate_decimal(sym("ASIN", node.args[0]))
            value = decimal_pi(work_precision) / 2 - asin_value
        elif node.op == "ATAN":
            value = decimal_atan(evaluate_decimal(node.args[0]), work_precision)
        elif node.op == "LN":
            argument = evaluate_decimal(node.args[0])
            if argument <= 0:
                raise ResolutionError(STATE_FORBIDDEN, "ln requires a positive value")
            value = argument.ln()
        elif node.op == "LOG10":
            argument = evaluate_decimal(node.args[0])
            if argument <= 0:
                raise ResolutionError(STATE_FORBIDDEN, "log10 requires a positive value")
            value = argument.log10()
        elif node.op == "LOG":
            argument = evaluate_decimal(node.args[0])
            base = evaluate_decimal(node.args[1])
            if argument <= 0 or base <= 0 or base == 1:
                raise ResolutionError(STATE_FORBIDDEN, "log requires value > 0, base > 0, and base != 1")
            value = argument.ln() / base.ln()
        elif node.op == "EXP":
            value = evaluate_decimal(node.args[0]).exp()
        else:
            raise ResolutionError(STATE_ABSTAIN, f"No decimal approximation rule for {node.op}")
        value = +value
        memo[key] = value
        return value

    with localcontext() as ctx:
        ctx.prec = work_precision
        return +evaluate_decimal(expr)

def exact_decimal_fraction(value: Fraction, limit: int) -> tuple[str, bool]:
    sign = "-" if value < 0 else ""
    value = abs(value)
    whole = value.numerator // value.denominator
    remainder = value.numerator % value.denominator
    if remainder == 0:
        return sign + str(whole), True
    digits: list[str] = []
    seen: set[int] = set()
    while remainder and len(digits) < limit:
        if remainder in seen:
            break
        seen.add(remainder)
        remainder *= 10
        digits.append(str(remainder // value.denominator))
        remainder %= value.denominator
    text = sign + str(whole) + "." + "".join(digits)
    return text + ("" if remainder == 0 else "…"), remainder == 0


def format_decimal(value: Decimal, precision: int) -> str:
    if value.is_zero():
        return "0"
    adjusted = value.adjusted()
    if adjusted >= precision or adjusted <= -6:
        text = format(value, f".{precision - 1}E")
    else:
        fractional = max(0, precision - adjusted - 1)
        text = format(value, f".{fractional}f")
    if "E" in text:
        mantissa, exponent = text.split("E", 1)
        mantissa = mantissa.rstrip("0").rstrip(".")
        exponent = exponent.lstrip("+").lstrip("0") or "0"
        if exponent.startswith("-"):
            exponent = "-" + (exponent[1:].lstrip("0") or "0")
        return f"{mantissa}e{exponent}"
    return text.rstrip("0").rstrip(".")


def resolve_expression(text: str, precision: int = DEFAULT_PRECISION) -> dict:
    precision = max(MIN_PRECISION, min(MAX_PRECISION, int(precision)))
    surface = text.strip()
    structure_canonical = "UNRESOLVED"
    records: list[dict] = []
    limit_info = None
    error_code = None
    internal_error_code = None
    exact = None
    approximate = None
    approximation_note = None
    display_kind = "UNRESOLVED"
    semantic_canonical = "UNRESOLVED"
    try:
        preflight_surface(surface)
        tokens = tokenize(surface)
        root = Parser(tokens).parse()
        count_ast_nodes(root)
        structure_canonical = canonical_node(root)
        result = evaluate(root, records, ResolutionBudget())
        exact = pretty_expr(result.expr) if result.expr is not None else None
        semantic_canonical = canonical_expr(result.expr) if result.expr is not None else result.state
        state = result.state
        note = result.note
        if result.expr is not None:
            try:
                if is_rat(result.expr):
                    assert result.expr.value is not None
                    approximate, finite = exact_decimal_fraction(result.expr.value, precision)
                    display_kind = "EXACT_RATIONAL_TERMINATING" if finite else "EXACT_RATIONAL_REPEATING"
                    approximation_note = "Exact terminating decimal" if finite else "Exact repeating rational decimal using ellipsis notation"
                else:
                    approximate = format_decimal(eval_decimal(result.expr, precision), precision)
                    display_kind = "APPROXIMATE_SYMBOLIC"
                    approximation_note = "Deterministic high-precision decimal approximation with guard precision; excluded from exact identity certificates"
            except ResolutionError as exc:
                if exc.state in {STATE_FORBIDDEN, STATE_SINGULAR, STATE_LIMIT_EXCEEDED}:
                    state = exc.state
                    note = exc.message
                    error_code = exc.code
                    limit_info = exc.details if exc.state == STATE_LIMIT_EXCEEDED else None
                    exact = None
                    approximate = None
                    approximation_note = None
                    semantic_canonical = state
                else:
                    approximation_note = exc.message
    except ResolutionError as exc:
        state = exc.state
        note = exc.message
        error_code = exc.code
        limit_info = exc.details if exc.state == STATE_LIMIT_EXCEEDED else None
        semantic_canonical = state
    except RecursionError:
        state = STATE_LIMIT_EXCEEDED
        note = "The expression exceeded the supported recursion boundary"
        error_code = "MAX_RECURSION_BOUNDARY"
        limit_info = {"max_nesting_depth": MAX_NESTING_DEPTH, "max_ast_nodes": MAX_AST_NODES}
        semantic_canonical = state
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        state = STATE_INTERNAL_ERROR
        note = "The resolver encountered an unexpected internal failure"
        internal_error_code = "SVARE_INTERNAL_001"
        semantic_canonical = state

    structure_certificate = sha256_text(
        f"SVARE|CERTIFICATE_SCHEMA|{CERTIFICATE_SCHEMA_VERSION}|CANONICALIZATION|{CANONICALIZATION_VERSION}|STRUCTURE|{structure_canonical}"
    )
    semantic_certificate = sha256_text(
        f"SVARE|CERTIFICATE_SCHEMA|{CERTIFICATE_SCHEMA_VERSION}|SEMANTIC_RULES|{SEMANTIC_RULES_VERSION}|SEMANTIC|{semantic_canonical}|{state}"
    )
    if state == STATE_EXACT_RATIONAL:
        display_value = approximate
        display_mathematical_form = exact
        display_form_label = "Exact mathematical form"
    elif state == STATE_EXACT_SYMBOLIC:
        display_value = f"≈ {approximate}" if approximate is not None else "approximation unavailable"
        display_mathematical_form = exact
        display_form_label = "Exact mathematical form"
    elif state in {STATE_SINGULAR, STATE_FORBIDDEN}:
        display_kind = "UNDEFINED"
        display_value = "undefined"
        display_mathematical_form = surface or "—"
        display_form_label = "Evaluated expression"
    elif state == STATE_INDETERMINATE:
        display_kind = "INDETERMINATE"
        display_value = "indeterminate"
        display_mathematical_form = surface or "—"
        display_form_label = "Evaluated expression"
    elif state == STATE_INCOMPLETE:
        display_kind = "INCOMPLETE"
        display_value = "incomplete"
        display_mathematical_form = surface or "—"
        display_form_label = "Submitted expression"
    elif state == STATE_ABSTAIN:
        display_kind = "NOT_EVALUATED"
        display_value = "not evaluated"
        display_mathematical_form = surface or "—"
        display_form_label = "Submitted expression"
    elif state == STATE_LIMIT_EXCEEDED:
        display_kind = "LIMIT_EXCEEDED"
        display_value = "limit exceeded"
        display_mathematical_form = surface or "—"
        display_form_label = "Submitted expression"
    elif state == STATE_INTERNAL_ERROR:
        display_kind = "INTERNAL_ERROR"
        display_value = "internal error"
        display_mathematical_form = surface or "—"
        display_form_label = "Submitted expression"
    else:
        display_kind = "UNRESOLVED"
        display_value = "unresolved"
        display_mathematical_form = surface or "—"
        display_form_label = "Submitted expression"

    display_certificate = sha256_text(
        f"SVARE|APPLICATION|{VERSION}|CERTIFICATE_SCHEMA|{CERTIFICATE_SCHEMA_VERSION}|DISPLAY|{semantic_certificate}|{precision}|"
        f"{display_kind}|{display_value or ''}|{display_form_label}|{display_mathematical_form or ''}"
    )

    return {
        "engine": ENGINE_NAME,
        "version": VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "semantic_rules_version": SEMANTIC_RULES_VERSION,
        "certificate_schema_version": CERTIFICATE_SCHEMA_VERSION,
        "resource_policy_version": RESOURCE_POLICY_VERSION,
        "conformance_vector_sha256": CONFORMANCE_VECTOR_SHA256,
        "surface": surface,
        "state": state,
        "resolution_class": (
            "EXACT_RATIONAL" if state == STATE_EXACT_RATIONAL else
            "EXACT_SYMBOLIC" if state == STATE_EXACT_SYMBOLIC else
            "LIMITED" if state == STATE_LIMIT_EXCEEDED else
            "FAILED" if state == STATE_INTERNAL_ERROR else
            "REFUSED"
        ),
        "display_kind": display_kind,
        "display_value": display_value,
        "display_mathematical_form": display_mathematical_form,
        "display_form_label": display_form_label,
        "resolved_value": display_value if state in {STATE_EXACT_RATIONAL, STATE_EXACT_SYMBOLIC} else None,
        "exact_mathematical_form": exact,
        "exact_value": exact,
        "decimal_approximation": approximate,
        "precision": precision,
        "precision_unit": "significant_digits",
        "note": note,
        "approximation_note": approximation_note,
        "error_code": error_code,
        "internal_error_code": internal_error_code,
        "limit": limit_info,
        "resource_policy": resource_policy(),
        "structure_canonical": structure_canonical,
        "semantic_canonical": semantic_canonical,
        "structure_certificate_sha256": structure_certificate,
        "semantic_certificate_sha256": semantic_certificate,
        "display_receipt_sha256": display_certificate,
        "records": records,
        "function_registry": sorted(FUNCTION_ARITY),
        "certificate_policy": "Structure and semantic certificates are versioned independently of display precision; display receipts include the application version, display precision, and display kind",
        "operator_policy": {
            "power_associativity": "right",
            "unary_minus_precedence": "below_power",
            "remainder_convention": "floor_division; remainder follows the divisor sign",
            "numeric_literal_alphabet": "ASCII digits 0-9",
        },
    }

def print_result(result: dict) -> None:
    print()
    print(f"SVARE v{result['version']}")
    print("=" * 78)
    print("Resolved value          :", result["display_value"])
    print(f"{result['display_form_label']:<24}:", result["display_mathematical_form"])
    print("Resolution class        :", result["resolution_class"])
    print("State                   :", result["state"])
    print("Precision               :", f"{result['precision']} significant digits")
    print("Note                    :", result["note"])
    if result.get("error_code"):
        print("Error code              :", result["error_code"])
    if result.get("internal_error_code"):
        print("Internal error code     :", result["internal_error_code"])
    if result.get("limit"):
        print("Limit details           :", json.dumps(result["limit"], sort_keys=True))
    if result["approximation_note"]:
        print("Approximation policy    :", result["approximation_note"])
    print("Structure certificate   :", result["structure_certificate_sha256"])
    print("Semantic certificate    :", result["semantic_certificate_sha256"])
    print("Display receipt         :", result["display_receipt_sha256"])
    print()
    print("Canonical structure")
    print(result["structure_canonical"])
    print()
    print("Canonical semantic value")
    print(result["semantic_canonical"])
    print()
    print("Resolution trace")
    print("-" * 78)
    for index, record in enumerate(result["records"], 1):
        trace_value = record["exact"]
        if trace_value is None:
            if record["state"] in {STATE_SINGULAR, STATE_FORBIDDEN}:
                trace_value = "undefined"
            elif record["state"] == STATE_INDETERMINATE:
                trace_value = "indeterminate"
            else:
                trace_value = "unresolved"
        print(f"{index:02d}. {record['state']} | {trace_value} | {record['note']}")


def conformance_payload_sha256(vectors: list[dict]) -> str:
    payload = {
        "schema_version": CONFORMANCE_VECTOR_SCHEMA_VERSION,
        "release_version": VERSION,
        "vectors": vectors,
    }
    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return sha256_text(canonical)


def self_test() -> dict:
    failures = []
    comparison_fields = (
        "state",
        "resolution_class",
        "exact_value",
        "decimal_approximation",
        "display_kind",
        "display_value",
        "display_mathematical_form",
        "display_form_label",
        "structure_canonical",
        "semantic_canonical",
        "structure_certificate_sha256",
        "semantic_certificate_sha256",
        "display_receipt_sha256",
        "error_code",
    )

    calculated_vector_hash = conformance_payload_sha256(CONFORMANCE_VECTORS)
    if calculated_vector_hash != CONFORMANCE_VECTOR_SHA256:
        failures.append(
            {
                "test": "embedded conformance vector hash",
                "expected": CONFORMANCE_VECTOR_SHA256,
                "actual": calculated_vector_hash,
            }
        )

    for vector in CONFORMANCE_VECTORS:
        result = resolve_expression(vector["expression"], vector["precision"])
        differences = {
            field: {"expected": vector["expected"].get(field), "actual": result.get(field)}
            for field in comparison_fields
            if vector["expected"].get(field) != result.get(field)
        }
        if differences:
            failures.append(
                {
                    "test": "conformance vector",
                    "id": vector["id"],
                    "expression": vector["expression"],
                    "differences": differences,
                }
            )

    equivalents = [resolve_expression(expression, 30) for expression in ("sin(pi/6)", "sin(deg(30))", "1/2")]
    if len({item["semantic_certificate_sha256"] for item in equivalents}) != 1:
        failures.append(
            {
                "test": "semantic equivalence",
                "actual": [item["semantic_certificate_sha256"] for item in equivalents],
            }
        )

    precision_20 = resolve_expression("sin(pi/6) + cos(pi) + sqrt(2) + ln(2)", 20)
    precision_60 = resolve_expression("sin(pi/6) + cos(pi) + sqrt(2) + ln(2)", 60)
    if not (
        precision_20["structure_certificate_sha256"] == precision_60["structure_certificate_sha256"]
        and precision_20["semantic_certificate_sha256"] == precision_60["semantic_certificate_sha256"]
        and precision_20["display_receipt_sha256"] != precision_60["display_receipt_sha256"]
        and precision_20["decimal_approximation"] != precision_60["decimal_approximation"]
    ):
        failures.append({"test": "precision isolation"})

    symbolic = resolve_expression("sqrt(2)", 30)
    if not str(symbolic["display_value"]).startswith("≈ "):
        failures.append(
            {
                "test": "symbolic approximation marker",
                "actual": symbolic["display_value"],
            }
        )

    adjacent_path = Path(__file__).with_name("SVARE_v10_0_6_vectors.json")
    external_vectors_checked = adjacent_path.exists()
    if external_vectors_checked:
        try:
            external = json.loads(adjacent_path.read_text(encoding="utf-8"))
            external_payload = {
                "schema_version": external.get("schema_version"),
                "release_version": external.get("release_version"),
                "vectors": external.get("vectors"),
            }
            external_hash = sha256_text(
                json.dumps(external_payload, ensure_ascii=False, separators=(",", ":"))
            )
            if (
                external.get("conformance_vector_sha256") != CONFORMANCE_VECTOR_SHA256
                or external_hash != CONFORMANCE_VECTOR_SHA256
                or external.get("vectors") != CONFORMANCE_VECTORS
            ):
                failures.append(
                    {
                        "test": "external conformance vector file",
                        "path": str(adjacent_path),
                        "expected_sha256": CONFORMANCE_VECTOR_SHA256,
                        "declared_sha256": external.get("conformance_vector_sha256"),
                        "calculated_sha256": external_hash,
                    }
                )
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(
                {
                    "test": "external conformance vector file",
                    "path": str(adjacent_path),
                    "error": str(exc),
                }
            )

    return {
        "version": VERSION,
        "conformance_vector_sha256": CONFORMANCE_VECTOR_SHA256,
        "external_vectors_checked": external_vectors_checked,
        "case_count": len(CONFORMANCE_VECTORS) + 4,
        "failure_count": len(failures),
        "all_pass": not failures,
        "failures": failures,
    }


def interactive(precision: int) -> None:
    print(f"SVARE v{VERSION} — enter an expression, or type exit.")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            return
        if text.lower() in {"exit", "quit"}:
            return
        if text:
            print_result(resolve_expression(text, precision))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=ENGINE_NAME)
    parser.add_argument("expression", nargs="*", help="Expression to resolve")
    parser.add_argument("--precision", type=int, default=DEFAULT_PRECISION, help=f"Decimal display precision ({MIN_PRECISION}-{MAX_PRECISION})")
    parser.add_argument("--json", action="store_true", help="Emit a JSON receipt")
    parser.add_argument("--self-test", action="store_true", help="Run the release self-test")
    parser.add_argument("--list-functions", action="store_true", help="List supported functions")
    parser.add_argument("--version", action="version", version=f"SVARE {VERSION}")
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        args.expression.extend(unknown)
    if args.list_functions:
        print("\n".join(sorted(FUNCTION_ARITY)))
        return 0
    if args.self_test:
        report = self_test()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["all_pass"] else 1
    expression = " ".join(args.expression).strip()
    if not expression and not sys.stdin.isatty():
        expression = sys.stdin.read().strip()
    if expression:
        result = resolve_expression(expression, args.precision)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print_result(result)
        return 0 if result["state"].startswith("RESOLVED") else 2
    if args.json:
        print(json.dumps(resolve_expression("", args.precision), indent=2, sort_keys=True))
        return 2
    interactive(args.precision)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        try:
            sys.stdout.close()
        finally:
            raise SystemExit(0)
