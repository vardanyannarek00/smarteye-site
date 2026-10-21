<?php
// Temporary diagnostic for the Telegram notification. Shows no secrets. Delete after setup.
header('Content-Type: text/plain; charset=UTF-8');

$cfg = __DIR__ . '/../smarteye-config.php';
echo "1. Ֆայլը (" . realpath(__DIR__ . '/..') . "/smarteye-config.php): " . (is_file($cfg) ? "ԿԱ" : "ՉԿԱ") . "\n";
if (!is_file($cfg)) {
    echo "\nՖայլը չի գտնվել։ Համոզվիր, որ այն /home/smarteye թղթապանակում է և կոչվում է ճիշտ smarteye-config.php\n";
    $near = glob(__DIR__ . '/../*config*') ?: [];
    if ($near) echo "Կողքի նման ֆայլեր: " . implode(', ', array_map('basename', $near)) . "\n";
    exit;
}

require $cfg;
$hasTok  = defined('TG_TOKEN') && TG_TOKEN !== '';
$hasChat = defined('TG_CHAT') && TG_CHAT !== '';
echo "2. TG_TOKEN: " . ($hasTok ? "լրացված (" . strlen(TG_TOKEN) . " նիշ, ձևաչափը " . (preg_match('/^\d+:[\w-]{30,}$/', TG_TOKEN) ? "ճիշտ" : "ՍԽԱԼ") . ")" : "ՉԿԱ") . "\n";
echo "3. TG_CHAT: " . ($hasChat ? TG_CHAT : "ՉԿԱ") . "\n";
echo "4. curl: " . (function_exists('curl_init') ? "կա" : "չկա") . "\n";
if (!$hasTok || !$hasChat) exit;

$ch = curl_init('https://api.telegram.org/bot' . TG_TOKEN . '/sendMessage');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15,
    CURLOPT_POSTFIELDS => http_build_query(['chat_id' => TG_CHAT, 'text' => '✅ SmartEye կայքի թեստ'])]);
$res = curl_exec($ch);
$err = curl_error($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($res === false) {
    echo "5. Կապ Telegram-ի հետ: ՉԿԱ — $err\n   (հոստինգը փակում է դեպի api.telegram.org կապը, պետք է գրել name.am-ին)\n";
    exit;
}
$j = json_decode($res, true);
echo "5. Telegram-ի պատասխան: HTTP $code — " . (!empty($j['ok']) ? "ՈՒՂԱՐԿՎԵՑ" : ($j['description'] ?? $res)) . "\n";

function tg($method) {
    $r = @file_get_contents('https://api.telegram.org/bot' . TG_TOKEN . '/' . $method);
    return $r ? json_decode($r, true) : null;
}
$me = tg('getMe');
echo "\n6. Բոտը, որին պատկանում է token-ը: @" . ($me['result']['username'] ?? '?') . "\n";
$wh = tg('getWebhookInfo');
echo "   webhook: " . (!empty($wh['result']['url']) ? "ԿԱ — " . parse_url($wh['result']['url'], PHP_URL_HOST) . " (այն «ուտում» է հաղորդագրությունները)" : "չկա") . "\n";
$up = tg('getUpdates');
echo "   getUpdates: " . ($up === null ? "պատասխան չկա" : (!empty($up['ok']) ? "ok, " . count($up['result']) . " հաղորդագրություն" : ($up['description'] ?? '?'))) . "\n";
$seen = [];
foreach (($up['result'] ?? []) as $u) {
    $c = $u['message']['chat'] ?? $u['my_chat_member']['chat'] ?? null;
    if ($c) $seen[$c['id']] = trim(($c['first_name'] ?? '') . ' @' . ($c['username'] ?? ''));
}
echo "7. Ովքեր են գրել այս բոտին վերջերս:\n";
if (!$seen) echo "   ոչ ոք (Start-ը սեղմվել է ուրիշ բոտում)\n";
foreach ($seen as $id => $n) echo "   ID $id — $n" . ($id == TG_CHAT ? "  ← համընկնում է" : "") . "\n";
