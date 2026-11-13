<?php
// SmartEye Price Manager — today's USD → AMD rate.
// 1) rate.am (bank rates: average / best selling rate for USD)  2) fallback: Central Bank of Armenia official rate.
// Result is cached for 30 minutes next to the site (outside public_html).

header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: public, max-age=900');

$cache = __DIR__ . '/../smarteye-rate-cache.json';
if (empty($_GET['fresh']) && is_file($cache) && time() - filemtime($cache) < 1800) { readfile($cache); exit; }

function http($url, $post = null, $headers = []) {
    $ch = curl_init($url);
    $h = array_merge(['User-Agent: Mozilla/5.0 (SmartEye Price Manager)', 'Accept-Language: hy,en;q=0.8'], $headers);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true, CURLOPT_TIMEOUT => 12, CURLOPT_HTTPHEADER => $h, CURLOPT_ENCODING => '']);
    if ($post !== null) { curl_setopt($ch, CURLOPT_POST, true); curl_setopt($ch, CURLOPT_POSTFIELDS, $post); }
    $r = curl_exec($ch); $c = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    return ($r !== false && $c >= 200 && $c < 300) ? $r : '';
}
function sane($v) { $v = (float)str_replace(',', '.', $v); return ($v > 250 && $v < 700) ? $v : 0; }

$out = ['ok' => false, 'at' => date('c'), 'src' => '', 'rate' => 0, 'cba' => 0, 'avgSell' => 0, 'bestSell' => 0, 'banks' => 0];

// --- Central Bank (official) ---
$soap = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ExchangeRatesLatest xmlns="http://www.cba.am/" /></soap:Body></soap:Envelope>';
$x = http('https://api.cba.am/exchangerates.asmx', $soap, ['Content-Type: text/xml; charset=utf-8', 'SOAPAction: "http://www.cba.am/ExchangeRatesLatest"']);
if ($x && preg_match('#<ISO>USD</ISO>\s*<Amount>(\d+)</Amount>\s*<Rate>([\d.,]+)</Rate>#', $x, $m)) {
    $out['cba'] = round(sane($m[2]) / max(1, (int)$m[1]), 2);
}

// --- rate.am: collect USD selling rates of banks ---
$sells = [];
$page = http('https://rate.am/am/armenian-dram-exchange-rates/banks');
if ($page) {
    // Next.js pages carry their data as JSON; look for USD objects with buy/sell numbers.
    if (preg_match_all('#"USD"\s*:\s*\{[^{}]*?"buy"\s*:\s*"?([\d.]+)"?[^{}]*?"sell"\s*:\s*"?([\d.]+)"?#i', $page, $mm, PREG_SET_ORDER)) {
        foreach ($mm as $q) { if ($s = sane($q[2])) $sells[] = $s; }
    }
    if (!$sells && preg_match_all('#USD[^0-9]{0,400}?(3\d\d(?:[.,]\d+)?)[^0-9]{1,200}?(3\d\d(?:[.,]\d+)?)#u', strip_tags($page), $mm, PREG_SET_ORDER)) {
        foreach (array_slice($mm, 0, 40) as $q) { $a = sane($q[1]); $b = sane($q[2]); if ($a && $b) $sells[] = max($a, $b); }
    }
}
if (count($sells) >= 3) {
    sort($sells);
    $out['banks'] = count($sells);
    $out['bestSell'] = $sells[0];
    $out['avgSell'] = round(array_sum($sells) / count($sells), 2);
}

if ($out['avgSell']) { $out['rate'] = $out['avgSell']; $out['src'] = 'rate.am (բանկերի միջին վաճառք)'; }
elseif ($out['cba']) { $out['rate'] = $out['cba']; $out['src'] = 'ԿԲ պաշտոնական'; }
$out['ok'] = $out['rate'] > 0;

$json = json_encode($out, JSON_UNESCAPED_UNICODE);
if ($out['ok']) { @file_put_contents($cache, $json); }
elseif (is_file($cache)) { readfile($cache); exit; }   // keep the last good value
echo $json;
