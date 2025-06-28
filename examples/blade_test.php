<?php
// Test des directives Blade qui ne doivent PAS déclencher d'erreur @ 

@if (Route::has('login'))
    <div class="sm:fixed sm:top-0 sm:right-0 p-6 text-right z-10">
        @auth
            <a href="{{ url('/home') }}" class="font-semibold">Home</a>
        @else
            <a href="{{ route('login') }}" class="font-semibold">Log in</a>
            @if (Route::has('register'))
                <a href="{{ route('register') }}" class="ml-4 font-semibold">Register</a>
            @endif
        @endauth
    </div>
@endif

@section('content')
    <div class="container">
        @foreach($users as $user)
            <p>{{ $user->name }}</p>
        @endforeach
        
        @can('edit', $user)
            <button>Edit</button>
        @endcan
    </div>
@endsection

// Ces @ DOIVENT déclencher des erreurs car ce sont de vraies suppressions d'erreurs PHP
$result = @file_get_contents($url);
$data = @unserialize($input);
$connection = @mysql_connect($host, $user, $pass);

// Mais pas ceux-ci qui sont dans des commentaires
// $test = @some_function(); // commentaire avec @
/* 
   $another = @another_function();
*/
?>
