<?php
// SmartEye System — website form handler.
// Receives the "Անվճար խորհրդատվություն" and "Կապ" forms and emails them to the business mailbox.

const TO_EMAIL   = 'info@smarteye.am';
const FROM_EMAIL = 'info@smarteye.am';   // same domain, so the mail is not flagged as spoofed
date_default_timezone_set('Asia/Yerevan');

// Telegram settings live OUTSIDE the website folder and outside GitHub (the repo is public):
// /home/smarteye/smarteye-config.php defining TG_TOKEN and TG_CHAT.
$cfg = __DIR__ . '/../smarteye-config.php';
if (is_file($cfg)) {
    require $cfg;
}

function tg_chat() {
    if (defined('TG_CHAT') && TG_CHAT !== '' && TG_CHAT !== 'auto') return TG_CHAT;
    $f = __DIR__ . '/../smarteye-tgchat.txt';   // written by tg-test.php after you message the bot
    return is_file($f) ? trim(file_get_contents($f)) : '';
}

function telegram($text) {
    $chat = tg_chat();
    if (!defined('TG_TOKEN') || TG_TOKEN === '' || $chat === '') {
        return false;
    }
    $url  = 'https://api.telegram.org/bot' . TG_TOKEN . '/sendMessage';
    $data = http_build_query(['chat_id' => $chat, 'text' => $text, 'disable_web_page_preview' => 1]);
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $data,
                                CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10]);
        $res  = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return $res !== false && $code === 200;
    }
    $ctx = stream_context_create(['http' => ['method' => 'POST', 'timeout' => 10,
        'header' => "Content-Type: application/x-www-form-urlencoded\r\n", 'content' => $data]]);
    return @file_get_contents($url, false, $ctx) !== false;
}

function telegram_photos($caption) {
    $chat = tg_chat();
    if (!defined('TG_TOKEN') || TG_TOKEN === '' || $chat === '' || empty($_FILES['photos']['tmp_name'])) {
        return 0;
    }
    $sent = 0;
    foreach (array_slice((array)$_FILES['photos']['tmp_name'], 0, 5) as $i => $tmp) {
        if (!is_uploaded_file($tmp) || filesize($tmp) > 10 * 1024 * 1024 || !@getimagesize($tmp)) {
            continue;
        }
        $ch = curl_init('https://api.telegram.org/bot' . TG_TOKEN . '/sendPhoto');
        curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
            CURLOPT_POSTFIELDS => ['chat_id' => $chat, 'caption' => $i === 0 ? $caption : '',
                                   'photo' => new CURLFile($tmp, 'image/jpeg', 'photo.jpg')]]);
        if (curl_exec($ch) !== false && curl_getinfo($ch, CURLINFO_HTTP_CODE) === 200) $sent++;
        curl_close($ch);
    }
    return $sent;
}

function back($status) {
    $ref = $_SERVER['HTTP_REFERER'] ?? '';
    $page = 'quote.html';
    if ($ref && preg_match('~/(index|quote|contact)\.html~', $ref, $m)) {
        $page = $m[1] . '.html';
    } elseif ($ref && preg_match('~^https?://[^/]+/?(\?.*)?$~', $ref)) {
        $page = 'index.html';
    }
    header('Location: ' . $page . '?sent=' . $status . '#form', true, 303);
    exit;
}

function field($name, $max = 500) {
    $v = trim((string)($_POST[$name] ?? ''));
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max, 'UTF-8');
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: quote.html', true, 302);
    exit;
}

// Spam trap: real visitors never see or fill this field.
if (field('website') !== '') {
    back('ok');
}

$form    = field('form', 20) === 'contact' ? 'contact' : 'quote';
$name    = field('name', 100);
$phone   = field('phone', 40);
$service = field('service', 120);
$subject = field('subject', 150);
$note    = field('note', 2000);
$message = field('message', 2000);

if ($name === '' || $phone === '' || !preg_match('/\d{6,}/', preg_replace('/\D/', '', $phone))) {
    back('err');
}

$lines = [
    'Անուն: '   . $name,
    'Հեռախոս: ' . $phone,
];
if ($form === 'quote') {
    $lines[] = 'Ծառայություն: ' . $service;
    if ($note !== '') $lines[] = "\nՄանրամասներ:\n" . $note;
    $title = 'Նոր հայտ կայքից — ' . ($service !== '' ? $service : 'Անվճար խորհրդատվություն');
} else {
    if ($subject !== '') $lines[] = 'Թեմա: ' . $subject;
    $lines[] = "\nՀաղորդագրություն:\n" . $message;
    $title = 'Նոր նամակ կայքից' . ($subject !== '' ? ' — ' . $subject : '');
}
$loc = field('loc', 200);
if ($loc !== '' && preg_match('~^https://maps\.google\.com/\?q=-?\d+(\.\d+)?,-?\d+(\.\d+)?$~', $loc)) {
    $lines[] = "\n📍 Տեղադրություն: " . $loc;
}
$nPhotos = empty($_FILES['photos']['tmp_name']) ? 0 : count(array_filter((array)$_FILES['photos']['tmp_name']));
if ($nPhotos) {
    $lines[] = "📷 Կցված նկարներ: " . min($nPhotos, 5) . " (ուղարկված են Telegram-ով)";
}
$lines[] = "\n—\nՈւղարկվել է smarteye.am-ից, " . date('Y-m-d H:i');

$headers = [
    'From: =?UTF-8?B?' . base64_encode('SmartEye կայք') . '?= <' . FROM_EMAIL . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];

$tg = telegram("🔔 " . $title . "\n\n" . implode("\n", $lines));
if ($tg) {
    telegram_photos('📷 ' . $name . ', ' . $phone);
}

$sent = mail(
    TO_EMAIL,
    '=?UTF-8?B?' . base64_encode($title) . '?=',
    implode("\n", $lines),
    implode("\r\n", $headers),
    '-f' . FROM_EMAIL
);

back(($sent || $tg) ? 'ok' : 'err');
