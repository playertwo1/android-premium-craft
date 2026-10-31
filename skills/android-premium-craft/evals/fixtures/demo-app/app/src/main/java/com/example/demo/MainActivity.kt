package com.example.demo

// App de teste com dados ficticios e falhas plantadas (F1..F13); ver PLANTED.md.
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class Entry(val id: Int, val name: String, val amount: String)

val sample = listOf(
    Entry(1, "Padaria Exemplo", "R$ 18,50"), Entry(2, "Mercado Ficticio", "R$ 120,00"),
    Entry(3, "Cliente Demo Ltda", "R$ 900,00"), Entry(4, "Assinatura Teste", "R$ 39,90"),
)

// F1 roxo padrao do Material; F2 onPrimary sem contraste sobre primary
val AppColors = lightColorScheme(primary = Color(0xFF6750A4), onPrimary = Color(0xFF9A86D0))

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = AppColors) { HomeScreen() } }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    var entries by remember { mutableStateOf(sample) }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Bem-vindo de volta! 👋") }, // F3 emoji
                actions = {
                    // F4 botao sem nome para TalkBack
                    IconButton(onClick = {}) { Icon(Icons.Default.Search, contentDescription = null) }
                    // Controle: botao correto, nao deve ser apontado
                    IconButton(onClick = {}) { Icon(Icons.Default.Add, contentDescription = "Adicionar lancamento") }
                },
            )
        },
    ) { _ -> // F5 innerPadding ignorado: conteudo fica sob a barra
        Column(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Color(0xFF6750A4), Color(0xFF3F51B5))))) { // F6 gradiente
            Text("SALDO ATUAL", fontSize = 10.sp, color = Color.White.copy(alpha = 0.4f)) // F7 10sp com alpha
            Card(Modifier.padding(13.dp).shadow(8.dp)) { // F8 card dentro de card e sombra
                Card(Modifier.padding(8.dp)) {
                    // F9 altura fixa corta o texto com fonte grande
                    Text("Unlock seamless insights", modifier = Modifier.height(20.dp).padding(horizontal = 8.dp))
                }
            }
            Box(Modifier.size(24.dp).background(Color.Yellow).clickable { entries = emptyList() }) // F10 alvo de 24dp que esvazia a lista
            Button(onClick = { entries = emptyList() }) { Text("Limpar") }
            // F11 lista sem key; lista vazia fica em branco, sem estado vazio
            LazyColumn { items(entries) { e -> Text("${e.name}  ${e.amount}", color = Color.White) } }
        }
    }
}
