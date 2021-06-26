<script>
	import { createEventDispatcher } from 'svelte';
	import Loading from  './Loading.svelte'
	import { fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	export let api;
	let name;
	let password;
	let error;
	let loading = false;

	async function login() {
		error = null;
		loading = true;
		api.login(name, password).then(() => dispatch('login')).catch(x => {error = x; loading=false})
		
	}

</script>
<main>
	<section>
<aside transition:fade>
	<center>
	<input type="text" bind:value={name} placeholder="Name"/>
	<input type="password" bind:value={password} placeholder="Password"/>
	<button on:click={login}>Login</button>
	<Loading enabled={loading}/>
	{#if error}
	<p>{error}</p>
	{/if}
</center>
</aside>
	</section>
</main>