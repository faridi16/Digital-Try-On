import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image } from 'react-native';
import FittingRoomRenderer from '../components/FittingRoomRenderer';

/**
 * Mock Wishlist Screen integrating the Digital Fitting Room UI.
 */
const WishlistScreen = () => {
  const [wishlistItems, setWishlistItems] = useState([
    { id: '1', name: 'Slim Fit Denim Jacket', brand: 'Roadster', price: '₹1499', type: 'jacket' },
    { id: '2', name: 'Floral Print Maxi Dress', brand: 'H&M', price: '₹2999', type: 'dress' },
  ]);

  const [activeFittingRoom, setActiveFittingRoom] = useState(null);
  const [fittingMode, setFittingMode] = useState('A'); // 'A' for Avatar, 'B' for AR Photo
  const [showFallback, setShowFallback] = useState(false);

  const handleTryItOn = (item, mode) => {
    setActiveFittingRoom(item.id);
    setFittingMode(mode);
    setShowFallback(false);
  };

  const handleTimeoutFallback = () => {
    console.log('Wishlist Screen: Handling fallback due to timeout/memory.');
    setShowFallback(true);
  };

  const renderItem = ({ item }) => {
    const isFitting = activeFittingRoom === item.id;

    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.itemName}>{item.name}</Text>
          <Text style={styles.itemBrand}>{item.brand}</Text>
          <Text style={styles.itemPrice}>{item.price}</Text>
        </View>

        {isFitting ? (
          showFallback ? (
            <View style={styles.fallbackContainer}>
              <Text style={styles.fallbackText}>⚠️ Device limit reached.</Text>
              <Text style={styles.fallbackSubText}>Showing static 2D preview instead.</Text>
              <View style={styles.vectorMockup}>
                 <Text>👕 2D Vector Representation</Text>
              </View>
              <TouchableOpacity style={styles.closeBtn} onPress={() => setActiveFittingRoom(null)}>
                <Text style={styles.closeBtnText}>Close</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.rendererWrapper}>
              <FittingRoomRenderer 
                item={item} 
                mode={fittingMode} 
                onTimeoutFallback={handleTimeoutFallback}
              />
              <TouchableOpacity style={styles.closeBtn} onPress={() => setActiveFittingRoom(null)}>
                <Text style={styles.closeBtnText}>Close Fitting Room</Text>
              </TouchableOpacity>
            </View>
          )
        ) : (
          <View style={styles.actionContainer}>
            {/* Task 5.1: "Try It On" UI components */}
            <TouchableOpacity 
              style={[styles.tryOnBtn, styles.btnAvatar]} 
              onPress={() => handleTryItOn(item, 'A')}
            >
              <Text style={styles.btnText}>👕 Try on Avatar (Mode A)</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.tryOnBtn, styles.btnAR]} 
              onPress={() => handleTryItOn(item, 'B')}
            >
              <Text style={styles.btnText}>📸 Try via AR (Mode B)</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>My Wishlist</Text>
      <FlatList
        data={wishlistItems}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    padding: 20,
    paddingTop: 50,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee'
  },
  listContent: {
    padding: 15,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 20,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardHeader: {
    padding: 15,
  },
  itemName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333'
  },
  itemBrand: {
    fontSize: 14,
    color: '#888',
    marginTop: 4
  },
  itemPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF3F6C', // Myntra typical color
    marginTop: 8
  },
  actionContainer: {
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#eee',
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  tryOnBtn: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 5
  },
  btnAvatar: {
    backgroundColor: '#5A67D8', // Indigo
  },
  btnAR: {
    backgroundColor: '#48BB78', // Green
  },
  btnText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 12
  },
  rendererWrapper: {
    padding: 15,
    backgroundColor: '#fafafa',
  },
  closeBtn: {
    marginTop: 15,
    padding: 12,
    backgroundColor: '#eee',
    borderRadius: 8,
    alignItems: 'center'
  },
  closeBtnText: {
    color: '#555',
    fontWeight: '600'
  },
  fallbackContainer: {
    padding: 20,
    backgroundColor: '#FFF5F5',
    alignItems: 'center'
  },
  fallbackText: {
    color: '#C53030',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  fallbackSubText: {
    color: '#718096',
    fontSize: 14,
    marginBottom: 15
  },
  vectorMockup: {
    width: '100%',
    height: 200,
    backgroundColor: '#EDF2F7',
    borderWidth: 2,
    borderColor: '#CBD5E0',
    borderStyle: 'dashed',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center'
  }
});

export default WishlistScreen;
