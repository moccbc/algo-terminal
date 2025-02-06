#include <bits/stdc++.h>
#define all(x) begin(x), end(x)
#define rall(x) rbegin(x), rend(x)
using namespace std;
using ll = long long;

template<class T> using pq_min = priority_queue<T,vector<T>,greater<T>>;
template<class T> using pq_max = priority_queue<T,vector<T>,less<T>>;

struct Card {
  int number = -1;
  int color = -1;
};

ll count(int pos, vector<int> &v, int &ct) {
  ct++;
  if (pos == -1){
    return 1LL;
  }

  ll res = 0;
  for (int i = 0; i < 12; i++) {
    if (pos + 1 == (int) v.size() || i < v[pos+1]) {
      v[pos] = i;
      res += count(pos-1, v, ct);
    }
  }

  return res;
}

ll count2(ll num, int depth, int &ct) {
  ct++;
  if (depth == 0) {
    return 1LL;
  }

  ll sum = 0;
  for (ll i = 1; i <= num; i++) {
    sum += count2(i, depth - 1, ct);
  }
  return sum;
}

ll count3(int pos, vector<array<int,2>> &v, int &ct, bool show) {
  ct++;
  if (pos == -1){
    if (show) {
      for (auto arr : v) {
        cout << "(" << arr[0] << " " << arr[1] << ") ";
      }
      cout << endl;
    }
    return 1LL;
  }

  ll res = 0;
  for (int i = 0; i < 12; i++) {
    for (int j = 0; j < 2; j++) {
      array<int,2> card = {i, j};
      if (pos + 1 == (int) v.size() || card < v[pos+1]) {
        v[pos] = card;
        res += count3(pos-1, v, ct, show);
      }
    }
  }

  return res;
}

ll choose(ll n, ll c) {
  if (c == 0) {
    return 1;
  }
  set<ll> numer, denom;
  for (int i = 1; i <= c; i++) {
    denom.insert(i);
    numer.insert(n - i + 1);
  }
  denom.erase(1);

  ll res = 1;
  for (auto x : numer) {
    res *= x;
    auto it = denom.rbegin();
    set<ll> toRemove;
    for (; it != denom.rend(); it++) {
      if (res % *it == 0) {
        res /= *it;
        toRemove.insert(*it);
      }
    }
    for (auto x : toRemove) {
      denom.erase(x);
    }
  }
  return res;
}

void solve() {
  int numberOfCards = 12;

  for (int n = 0; n <= numberOfCards; n++) {
    cout << n << endl;

    int countForCount = 0;
    vector<int> v(n, 0);
    cout << count(n-1, v, countForCount) << endl;

    int countForCount2 = 0;
    ll outerLoop = numberOfCards - n + 1;
    cout << count2(outerLoop, n, countForCount2) << endl;

    int countForCount2a = 0;
    ll outerLoopa = 2*numberOfCards - n + 1;
    cout << count2(outerLoopa, n, countForCount2a) << endl;

    int countForCount3 = 0;
    vector<array<int,2>> vv(n);
    cout << count3(n-1, vv, countForCount3, false) << endl;

    cout << choose(numberOfCards*2, n) << endl;

    cout << countForCount << " " << countForCount2 << " " << countForCount2a << " " << countForCount3 << endl;
    cout << endl;
  }

  int m = 2;
  int cards = 24;
  int countForCount2 = 0;
  ll outerLoop = cards - m + 1;
  cout << count2(outerLoop, m, countForCount2) << endl;

  int countForCount3 = 0;
  vector<array<int,2>> vv(m);
  cout << count3(m-1, vv, countForCount3, true) << endl;

  set<Card> opponentHand = {
    {0, 0}
  };

  set<Card> yourHand = {
    {1, 1}
  };

}

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(0);
  int t = 1;
  // cin >> t;
  while (t--) solve();
  #ifdef LOCAL_TIME
    cerr << "Time elapsed: " << 1.0 * clock() / CLOCKS_PER_SEC << "s\n";
  #endif
}
