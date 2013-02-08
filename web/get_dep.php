<?php
$graph = json_decode(file_get_contents("all.json"), true);
$rfc = $_GET['rfc'];
$rfc = preg_replace('/[^0-9]/', '', $rfc, $count);
if($count != 0 || !array_key_exists($rfc, $graph)) {
	die();
}
$result["from"]=$rfc;
$result["title"] = $graph[$rfc]["title"];
#print_r($graph[$rfc]);print("<br>");
foreach ($graph[$rfc]["refs"] as $ref) {
	$result["refs"][$ref] = $graph[$ref]["title"];
}
print json_encode($result);
?>