<?php
// SmartEye Price Manager — archive old quotes to the business Telegram chat.
// Only a signed-in Price Manager user can call it: the Supabase login token is checked against Supabase itself.
// Telegram token/chat come from /home/smarteye/smarteye-config.php (outside the public repo), same as send.php.

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }

const SB_URL = 'https://cdtkvqrdmdkcsymdsxgc.supabase.co';
const SB_KEY = 'sb_publishable_wmwBKpRHvvH8cTbXl34jOw_rfJym2I2';   // public key (same as in the app)
const PM_USERS = ['b628c0cd-1aa7-46d0-ad04-de19fb51cee2'];        // Price Manager accounts allowed to archive

$cfg = __DIR__ . '/../smarteye-config.php';
if (is_file($cfg)) { require $cfg; }

function out($ok, $err = '') { echo json_encode(['ok' => $ok, 'err' => $err]); exit; }

$token = trim((string)($_POST['token'] ?? ''));
$text  = trim((string)($_POST['text'] ?? ''));
if ($token === '' || $text === '') { http_response_code(400); out(false, 'empty'); }

// who is calling?
$ch = curl_init(SB_URL . '/auth/v1/user');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
    CURLOPT_HTTPHEADER => ['apikey: ' . SB_KEY, 'Authorization: Bearer ' . $token]]);
$res = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
$user = $code === 200 ? json_decode($res, true) : null;
$allowed = defined('PM_UIDS') ? PM_UIDS : PM_USERS;
if (!$user || empty($user['id']) || !in_array($user['id'], $allowed, true)) { http_response_code(403); out(false, 'auth'); }

$chat = (defined('TG_ARCHIVE_CHAT') && TG_ARCHIVE_CHAT !== '') ? TG_ARCHIVE_CHAT
      : ((defined('TG_CHAT') && TG_CHAT !== '' && TG_CHAT !== 'auto') ? TG_CHAT
      : (is_file(__DIR__ . '/../smarteye-tgchat.txt') ? trim(file_get_contents(__DIR__ . '/../smarteye-tgchat.txt')) : ''));
if (!defined('TG_TOKEN') || TG_TOKEN === '' || $chat === '') { http_response_code(503); out(false, 'telegram not configured'); }

$text = mb_substr($text, 0, 4000);
$ch = curl_init('https://api.telegram.org/bot' . TG_TOKEN . '/sendMessage');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15,
    CURLOPT_POSTFIELDS => http_build_query(['chat_id' => $chat, 'text' => $text, 'disable_web_page_preview' => 1])]);
$r = curl_exec($ch); $c = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
if ($r === false || $c !== 200) { http_response_code(502); out(false, 'telegram ' . $c); }
out(true);
