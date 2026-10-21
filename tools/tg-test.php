<?php
// Telegram setup page. Shows no secrets. Finds who messaged the bot, saves that chat, sends a test.
header('Content-Type: text/plain; charset=UTF-8');

$cfg = __DIR__ . '/../smarteye-config.php';
if (!is_file($cfg)) { echo "✗ /home/smarteye/smarteye-config.php ֆայլը չկա\n"; exit; }
require $cfg;
if (!defined('TG_TOKEN') || !preg_match('/^\d+:[\w-]{30,}$/', TG_TOKEN)) { echo "✗ TG_TOKEN-ը սխալ է կամ դատարկ\n"; exit; }

function tg($method, $params = []) {
    $ch = curl_init('https://api.telegram.org/bot' . TG_TOKEN . '/' . $method);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($params),
                            CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
    $r = curl_exec($ch); curl_close($ch);
    return $r ? json_decode($r, true) : ['ok' => false, 'description' => 'կապ չկա api.telegram.org-ի հետ'];
}

$me = tg('getMe');
if (empty($me['ok'])) { echo "✗ Token-ը չի աշխատում: " . ($me['description'] ?? '') . "\n"; exit; }
echo "✓ Բոտը: @" . $me['result']['username'] . "\n";

$wh = tg('getWebhookInfo');
if (!empty($wh['result']['url'])) { tg('deleteWebhook'); echo "✓ Հին webhook-ը անջատվեց\n"; }

$up = tg('getUpdates');
$chats = [];
foreach (($up['result'] ?? []) as $u) {
    $c = $u['message']['chat'] ?? $u['my_chat_member']['chat'] ?? null;
    if ($c) $chats[$c['id']] = trim(($c['first_name'] ?? $c['title'] ?? '') . ' @' . ($c['username'] ?? ''));
}
$save = __DIR__ . '/../smarteye-tgchat.txt';
if ($chats) {
    $id = array_key_last($chats);
    file_put_contents($save, $id);
    echo "✓ Բոտին գրել է: " . $chats[$id] . " (ID $id) — պահպանվեց\n";
} elseif (is_file($save)) {
    $id = trim(file_get_contents($save));
    echo "✓ Պահպանված ID: $id\n";
} else {
    echo "✗ Բոտին դեռ ոչ ոք չի գրել։ Telegram-ում բացիր @" . $me['result']['username'] . ", գրիր «բարև», հետո թարմացրու այս էջը\n";
    exit;
}

$r = tg('sendMessage', ['chat_id' => $id, 'text' => '✅ SmartEye կայքի թեստ — կայքի հայտերը կգան այստեղ']);
echo !empty($r['ok']) ? "✓ Թեստային հաղորդագրությունը ՈՒՂԱՐԿՎԵՑ\n" : "✗ Չուղարկվեց: " . ($r['description'] ?? '') . "\n";
