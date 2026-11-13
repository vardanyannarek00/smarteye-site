<?php
// SmartEye Price Manager — website requests (from send.php) for the signed-in Price Manager user.
// GET  ?token=…            → latest requests
// POST token=…&done=<id>   → mark a request as handled
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

const SB_URL = 'https://cdtkvqrdmdkcsymdsxgc.supabase.co';
const SB_KEY = 'sb_publishable_wmwBKpRHvvH8cTbXl34jOw_rfJym2I2';   // public key (same as in the app)
const PM_USERS = ['b628c0cd-1aa7-46d0-ad04-de19fb51cee2'];

$cfg = __DIR__ . '/../smarteye-config.php';
if (is_file($cfg)) { require $cfg; }
function out($a, $code = 200) { http_response_code($code); echo json_encode($a, JSON_UNESCAPED_UNICODE); exit; }

$token = trim((string)($_POST['token'] ?? $_GET['token'] ?? ''));
if ($token === '') out(['ok' => false, 'err' => 'auth'], 401);
$ch = curl_init(SB_URL . '/auth/v1/user');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10, CURLOPT_HTTPHEADER => ['apikey: ' . SB_KEY, 'Authorization: Bearer ' . $token]]);
$res = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
$user = $code === 200 ? json_decode($res, true) : null;
$allowed = defined('PM_UIDS') ? PM_UIDS : PM_USERS;
if (!$user || empty($user['id']) || !in_array($user['id'], $allowed, true)) out(['ok' => false, 'err' => 'auth'], 403);

$file = __DIR__ . '/../smarteye-leads.jsonl';
$doneFile = __DIR__ . '/../smarteye-leads-done.json';
$done = is_file($doneFile) ? (json_decode(file_get_contents($doneFile), true) ?: []) : [];

if (!empty($_POST['done'])) {
    $id = preg_replace('/[^a-f0-9]/', '', (string)$_POST['done']);
    if ($id !== '') { $done[$id] = date('c'); file_put_contents($doneFile, json_encode($done), LOCK_EX); }
    out(['ok' => true]);
}

$rows = [];
if (is_file($file)) {
    $lines = array_slice(file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES), -200);
    foreach (array_reverse($lines) as $l) {
        $r = json_decode($l, true);
        if (!$r || empty($r['id'])) continue;
        $r['done'] = isset($done[$r['id']]);
        $rows[] = $r;
    }
}
out(['ok' => true, 'leads' => $rows]);
