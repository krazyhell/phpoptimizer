<?php
// Fichier d'exemple avec problèmes XPath et parsing XML/HTML

class XMLPerformanceIssues {
    
    // Problème 1: XPath inefficaces dans des boucles
    public function processXMLData($xmlFiles) {
        $results = [];
        
        foreach ($xmlFiles as $file) {
            $doc = new DOMDocument();
            $doc->load($file);
            $xpath = new DOMXPath($doc);
            
            // Très inefficace: sélecteur universel descendant
            $nodes = $xpath->query('//*[@id]');  // Pattern //*
            
            foreach ($nodes as $node) {
                // Encore plus inefficace: double descendant dans une boucle imbriquée
                $children = $xpath->query('.//child//*');  // Double descendant
                
                // XPath avec contains() sur descendant - très lent
                $matches = $xpath->query('//div[contains(@class, "active")]//span');
                
                // Axe descendant explicite - très coûteux
                $descendants = $xpath->query('./descendant::*[@data-value]');
                
                $results[] = ['node' => $node, 'children' => $children, 'matches' => $matches];
            }
        }
        return $results;
    }
    
    // Problème 2: Requêtes DOM répétées dans des boucles
    public function processHTMLElements($html, $selectors) {
        $doc = new DOMDocument();
        $doc->loadHTML($html);
        
        $elements = [];
        foreach ($selectors as $selector) {
            // getElementById dans une boucle
            $element = $doc->getElementById($selector);
            
            // getElementsByTagName dans une boucle  
            $tags = $doc->getElementsByTagName('div');
            
            foreach ($tags as $tag) {
                // XPath evaluate dans boucle imbriquée
                $xpath = new DOMXPath($doc);
                $result = $xpath->evaluate('count(.//*)');  // Compte tous les descendants
                
                $elements[] = ['element' => $element, 'count' => $result];
            }
        }
        return $elements;
    }
    
    // Problème 3: Regex inefficaces
    public function validateData($texts) {
        $valid = [];
        
        foreach ($texts as $text) {
            // Regex avec .* très lente
            if (preg_match('/start.*end/', $text)) {
                $valid[] = $text;
            }
            
            // Regex avec groupe capturant .* inefficace
            if (preg_match('/prefix(.*)suffix/', $text, $matches)) {
                $processed = preg_replace('/old.*pattern/', 'new', $matches[1]);
                $valid[] = $processed;
            }
            
            // Combinaison .+ et .* problématique
            if (preg_match('/begin.+middle.*end/', $text)) {
                $valid[] = 'complex: ' . $text;
            }
        }
        return $valid;
    }
    
    // Problème 4: XPath avec axes coûteux
    public function findRelatedNodes($doc, $contextNodes) {
        $xpath = new DOMXPath($doc);
        $related = [];
        
        foreach ($contextNodes as $node) {
            // Axe following:: très coûteux
            $following = $xpath->query('./following::div', $node);
            
            // Axe preceding:: très coûteux  
            $preceding = $xpath->query('./preceding::span', $node);
            
            // position() dans descendant très lent
            $positioned = $xpath->query('.//li[position() > 5]', $node);
            
            $related[] = [
                'following' => $following,
                'preceding' => $preceding, 
                'positioned' => $positioned
            ];
        }
        
        return $related;
    }
    
    // Problème 5: Combinaisons XPath particulièrement inefficaces
    public function complexXPathQueries($xmlContent) {
        $doc = new DOMDocument();
        $doc->loadXML($xmlContent);
        $xpath = new DOMXPath($doc);
        
        // Triple inefficacité: descendant + attribut + descendant
        $complex1 = $xpath->query('//item[@type]//child//subchild');
        
        // Sélecteur universel avec contains
        $complex2 = $xpath->query('//*[contains(text(), "search")]');
        
        // Axe following avec descendant
        $complex3 = $xpath->query('//node/following::*//descendant');
        
        return [$complex1, $complex2, $complex3];
    }
}

// Exemples d'usage avec SimpleXML aussi
function processSimpleXML($xmlString) {
    $xml = simplexml_load_string($xmlString);
    
    // XPath sur SimpleXML avec pattern inefficace
    $nodes = $xml->xpath('//*[@active="true"]//value');  // Double problème
    
    foreach ($nodes as $node) {
        // Encore une requête XPath dans la boucle
        $children = $xml->xpath('.//child');
        
        echo $node . "\n";
    }
}

// Ligne très très très très très très très très très très très très très très très très très très très très très très très très très très très très très longue qui dépasse 120 caractères
?>
