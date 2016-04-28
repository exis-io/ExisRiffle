package io.exis.cards.cards;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import android.content.Context;
import android.os.CountDownTimer;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.exis.riffle.Domain;
import com.exis.riffle.Riffle;

/**
 * Dealer.java
 * Manages decks and player points
 * TODO register methods joined and closed
 *
 * Created by luke on 10/13/15.
 */
public class Dealer extends Domain{

    final int ROOMCAP = 5;
    private ArrayList<Player> players;                      // keep track of players playing
    private Map answers;                                    // cards sent to czar
    private static ArrayList<Card> questionDeck;
    private static ArrayList<Card> answerDeck;
    private String phase;
    private static Player winner;                           // winner
    private static Card winningCard;
    private Card questionCard;                              // always know question card
    private String dealerID;
    int czarNum;
    private int dummyCount;
    private int playerCount;
    private int duration;
    private Handler handler;
    public Runnable runnable;
    Domain riffle;

    private Player player;

    public Dealer(int ID, Domain domain, Domain riffle){
        super("dealer" + ID, domain);
        this.riffle = riffle;
        dealerID = ID + "";
        czarNum = 0;
        players  = new ArrayList<>();
        answerDeck = MainActivity.getAnswers();
        questionDeck = MainActivity.getQuestions();
        questionCard = generateQuestion();

        answers = new HashMap<String, Card>();
        dummyCount = 0;
        playerCount = 0;
        duration = 15;
        phase = "answering";

        handler = GameActivity.handler;
    }//end Dealer constructor

    // riffle calls
    @Override
    public void onJoin(){
        Log.i("dealer onJoin", "entering method");

        register("leave", String.class, Object.class, (p) -> {
            return this.leave(p);
        });

        Log.i("dealer::onJoin", player.playerID() + " joining");
        player.join();
    }
    public String ID(){
        return this.dealerID;
    }
    public void addPlayer(Player player){
        //if max capacity exceeded
        if(full()){
            Log.i("dealer", "game is full");
            if(player.dummy){
                return;
            }else{
                removeDummy();
                Log.i("dealer", "adding player " + player.playerID());
                addPlayer(player);
            }
        }

        //deal them 5 cards
        for(int i=0; i<5; i++){
            dealCard(player);
        }

        if(!player.dummy) {
            playerCount++;
            this.player = player;
            player.domain().subscribe("picked", String.class, (c) -> {
                Log.i("picked listener", "received card " + c);
                answers.put(player.playerID(), new Card(c));
            });

/*
            player.domain().subscribe("chose", String.class, (c) -> {
                Log.i("choose listener", "received card " + c);
                winningCard = new Card(c);
            });
*/
        }
        players.add(player);
        publish("joined", player.playerID());
    }//end addPlayer method
    // returns current czar
    private Player czar(){
        return players.get(czarNum);
    }
    public Card dealCard(Player player){

        Card card = generateAnswer();                       //generate new card to give to player

        if(!player.dummy) {
            riffle.call("draw", card.getText());
        }else{
            player.draw(card.getText());                            //add card to player's hand
        }
        return card;
    }//end dealCard method
    public boolean full() {
        return players.size() == ROOMCAP;
    }
    public static Card generateQuestion(){
        Collections.shuffle(questionDeck);
        return questionDeck.get(0);
    }//end generateCard method
    public static Card generateAnswer(){
        Collections.shuffle(answerDeck);
        return answerDeck.get(0);
    }//end generateCard method
    public ArrayList<Card> getNewHand(){
        ArrayList<Card> hand = new ArrayList<>();
        Card newCard = generateAnswer();
        for(int i=0; i<5; i++){
            while(hand.contains(newCard)) {
                newCard = generateAnswer();
            }

            hand.add(generateAnswer());
        }

        return hand;
    }// end getNewHand method
    public Player[] getPlayers(){
        return players.toArray(new Player[players.size()]);
    }//end getPlayers method
    public Card getQuestion(){
        if(questionCard == null){
            questionCard = generateQuestion();
        }
        return questionCard;
    }
    public void prepareGame(){
        if(questionDeck == null) {
            questionDeck = MainActivity.getQuestions();                //load all questions
        }
        if(answerDeck == null) {
            answerDeck = MainActivity.getAnswers();                    //load all answers
        }
        Log.i("prepareGame", "questions has size " + questionDeck.size() +
                ", answers has size " + answerDeck.size());
    }
    public void addDummies(){                                   // add dummies to fill room
        while(players.size() < ROOMCAP){
            addPlayer(new Player());
            dummyCount++;
        }
    }
    private void removeDummy(){
        for(Player p: players){
            if(p.dummy){
                players.remove(p);
                return;
            }
        }
    }
    public Object leave(String leavingPlayer){
        for(Player p: players){
            if(p.playerID().equals(leavingPlayer)){
                players.remove(p);
            }
        }
        if(playerCount == 0){
            Exec.removeDealer(this);
        }
        publish("left", leavingPlayer);
        return null;
    }//end remove player method
    public void setPlayers(){                           // deal cards to all players
        for(int i=0; i<players.size(); i++){
            //give everyone 5 cards
            while(players.get(i).hand().size() < 5){
                dealCard(players.get(i));
            }
        }
    }//end setPlayers method
    private void setWinner(String winningCard){                     // dummies pick random winner
        if(player.isCzar()){
            for(Player p:players){
                if( winningCard.equals( answers.get(p.playerID()) ) ){
                    winner = p;
                }
            }
        }else{ // choose random player
            int num = (int)(Math.random()*5);
            while(players.get(num).isCzar()){
                num = (int)(Math.random()*5);
            }
            winner = players.get(num);
            this.winningCard = (Card) answers.get(winner.playerID());
        }
    }
    private void updateCzar(){                          //update czar to next player
        players.get(czarNum).setCzar(false);
        Log.d("update czar", "player " + czarNum + " (" + players.get(czarNum).playerID() + ") no longer czar");
        czarNum++;
        czarNum = czarNum % players.size();
        Log.d("update czar", "player " + czarNum + " (" + players.get(czarNum).playerID() + ") set to czar");
        players.get(czarNum).setCzar(true);
    }// end updateCzar method

    public Object[] play(){
        if(getPlayers().length < ROOMCAP){
            addDummies();
        }

        return new Object[]{
                Card.handToStrings( getNewHand() ),             // String[] cards
                getPlayers(),                                   // Player[] players
                phase,                                          // String   state
                dealerID};                                      // String   roomName
    }

    public void start(){
        //fill room with players
        addDummies();
        int delay = 15000;
        runnable = new Runnable(){
            public void run() {
                playGame(phase);
                handler.postDelayed(this, delay);
            }
        };
        handler.postDelayed(runnable, 0);
    }//end start method

    /* Main game logic.
     *
     * Answering - players submit cards to dealer
     * Picking - Czar picks winner
     * Scoring - Dealer announces winner
     *
     */
    private void playGame(String type){
        String TAG = "playGame";

        switch(type){
            case "answering":
                updateCzar();
                questionCard = generateQuestion();              //update question

                Log.i(TAG, "publishing [answering, \n" +
                        czar().playerID() + ", \n" +
                        getQuestion().getText() + ", \n" +
                        duration + "]");
                publish("answering", czar().playerID(), getQuestion().getText(), duration);

                setPlayers();                    // deal cards back to each player
                phase = "picking";

                break;
            case "picking":
                answers.clear();
                Log.i(TAG, "gathering answers from " + players.size() + " players");
                for(Player p : players){
                    if(p.dummy && !p.isCzar()) {
                        answers.put(p.playerID(), generateAnswer());
                    }
                }

                if(!player.isCzar()) {
                    Card card = generateAnswer();
                    Log.i("dealer picking phase", "calling pick with card " + card.getText());
                    player.domain().call("pick", card.getText()).then(String.class, (c) -> {
                        answers.put(player.playerID(), new Card(c));
                        while (answers.size() < 4) {
                            Log.wtf("padding answers pile", "answers had size " + answers.size());
                            answers.put(player.playerID(), generateAnswer());
                        }

                        ArrayList<Card> a = new ArrayList<Card>(answers.values());
                        Log.i(TAG, "publishing [picking, " +
                                Card.printHand(a) + "\n" +
                                duration + "]");
                        publish("picking", Card.serialize(Card.handToStrings(a)), duration);

                        phase = "scoring";
                    });
                }else{
                    ArrayList<Card> a = new ArrayList<Card>(answers.values());
                    Log.i(TAG, "publishing [picking, \n" +
                            Card.printHand(a) + "\n" +
                            duration + "]");
                    publish("picking", Card.serialize(Card.handToStrings(a)), duration);

                    phase = "scoring";
                }

                break;
            case "scoring":
                if(player.isCzar()){
                    player.domain().call("pick", "").then(String.class, (c)->{
                        setWinner(c);

                        Log.i(TAG, "publishing [scoring, " +
                                winner.playerID() + ", " +
                                winningCard.getText() + ", " +
                                duration + "]");
                        publish("scoring", winner.playerID(), winningCard.getText(), duration);

                        answers.clear();
                        phase = "answering";
                    });
                }else{
                    setWinner("");

                    if(winningCard == null){                // danger
                        Log.wtf("dealer scoring phase", "setWinner produced null card");
                        winningCard = generateAnswer();
                    }

                    Log.i(TAG, "publishing [scoring, " +
                            winner.playerID() + ", " +
                            winningCard.getText() + ", " +
                            duration + "]");
                    publish("scoring", winner.playerID(), winningCard.getText(), duration);

                    answers.clear();
                    phase = "answering";
                }



                break;
        }
    }// end playGame method
}//end Dealer class