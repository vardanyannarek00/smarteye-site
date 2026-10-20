<?php
// SmartEye System — website form handler.
// Receives the "Անվճար առաջարկ" and "Կապ" forms and emails them to the business mailbox.

const TO_EMAIL   = 'info@smarteye.am';
const FROM_EMAIL = 'info@smarteye.am';   // same domain, so the mail is not flagged as spoofed
date_default_timezone_set('Asia/Yerevan');

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
    $title = 'Նոր հայտ կայքից — ' . ($service !== '' ? $service : 'Անվճար առաջարկ');
} else {
    if ($subject !== '') $lines[] = 'Թեմա: ' . $subject;
    $lines[] = "\nՀաղորդագրություն:\n" . $message;
    $title = 'Նոր նամակ կայքից' . ($subject !== '' ? ' — ' . $subject : '');
}
$lines[] = "\n—\nՈւղարկվել է smarteye.am-ից, " . date('Y-m-d H:i');

$headers = [
    'From: =?UTF-8?B?' . base64_encode('SmartEye կայք') . '?= <' . FROM_EMAIL . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];

$sent = mail(
    TO_EMAIL,
    '=?UTF-8?B?' . base64_encode($title) . '?=',
    implode("\n", $lines),
    implode("\r\n", $headers),
    '-f' . FROM_EMAIL
);

back($sent ? 'ok' : 'err');
