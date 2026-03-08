<?php
/**
 * Figment Website — Enquiry Form Handler
 * Receives form submissions and creates tasks in ClickUp (Figment Database list)
 *
 * SETUP INSTRUCTIONS:
 * 1. Replace YOUR_CLICKUP_API_TOKEN_HERE with your ClickUp Personal API Token
 *    → Get it from: ClickUp → Profile Avatar → Settings → Apps → API Token
 * 2. Upload this file to your GoDaddy hosting root (same folder as index.html)
 * 3. Done. Forms will now create tasks in your Figment Database list.
 */

// ─── CONFIGURATION ───────────────────────────────────────────────────────────
define('CLICKUP_API_TOKEN', 'YOUR_CLICKUP_API_TOKEN_HERE');
define('CLICKUP_LIST_ID',   '901605214737'); // Figment Database
define('ALLOWED_ORIGIN',    'https://figment.global');
// ─────────────────────────────────────────────────────────────────────────────

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only allow POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

// Parse JSON body
$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    $input = $_POST; // fallback for form-encoded
}

// Sanitize inputs
function sanitize($val) {
    return htmlspecialchars(strip_tags(trim($val ?? '')), ENT_QUOTES, 'UTF-8');
}

$firstName  = sanitize($input['firstName'] ?? '');
$lastName   = sanitize($input['lastName'] ?? '');
$email      = sanitize($input['email'] ?? '');
$phone      = sanitize($input['phone'] ?? '');
$program    = sanitize($input['program'] ?? '');
$target     = sanitize($input['target'] ?? '');
$message    = sanitize($input['message'] ?? '');
$submittedAt = date('d M Y, h:i A');

// Validate required fields
if (empty($firstName) || empty($email)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Name and email are required']);
    exit;
}

$fullName = trim("$firstName $lastName");

// ── Build ClickUp task ────────────────────────────────────────────────────────
$taskName = "Website Enquiry — $fullName" . ($program ? " · $program" : '');

$description = "## Website Enquiry — figment.global\n\n";
$description .= "**Submitted:** $submittedAt\n\n";
$description .= "---\n\n";
$description .= "### Contact Details\n";
$description .= "**Name:** $fullName\n";
$description .= "**Email:** $email\n";
$description .= ($phone   ? "**Phone:** $phone\n"          : '');
$description .= "\n### Enquiry Details\n";
$description .= ($program ? "**Program of Interest:** $program\n" : '');
$description .= ($target  ? "**Target Country / University:** $target\n" : '');
$description .= ($message ? "\n### Message\n$message\n" : '');
$description .= "\n---\n*Submitted via figment.global contact form*";

$taskPayload = [
    'name'        => $taskName,
    'description' => $description,
    'status'      => 'to do',
    'priority'    => 2, // high
    'tags'        => ['website-enquiry'],
    'custom_fields' => []
];

// ── Call ClickUp API ─────────────────────────────────────────────────────────
$url = 'https://api.clickup.com/api/v2/list/' . CLICKUP_LIST_ID . '/task';

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => json_encode($taskPayload),
    CURLOPT_HTTPHEADER     => [
        'Authorization: ' . CLICKUP_API_TOKEN,
        'Content-Type: application/json',
    ],
    CURLOPT_TIMEOUT        => 15,
    CURLOPT_SSL_VERIFYPEER => true,
]);

$response   = curl_exec($ch);
$httpCode   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError  = curl_error($ch);
curl_close($ch);

// ── Respond to client ────────────────────────────────────────────────────────
if ($curlError) {
    error_log("figment/submit.php curl error: $curlError");
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Connection error. Please email us directly at info@figment.global']);
    exit;
}

$responseData = json_decode($response, true);

if ($httpCode === 200 && isset($responseData['id'])) {
    echo json_encode([
        'success'  => true,
        'message'  => 'Enquiry received! We will be in touch within 24 hours.',
        'task_id'  => $responseData['id']
    ]);
} else {
    error_log("figment/submit.php ClickUp error $httpCode: $response");
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Something went wrong. Please email us directly at info@figment.global',
        'debug'   => $httpCode
    ]);
}
?>
